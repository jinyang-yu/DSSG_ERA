import fitz 
import os
from pathlib import Path
from utils import text_preprocessing
from utils import table_of_contents
from utils import chunking
import pytesseract
import re
from collections import defaultdict, Counter
from pdf2image import convert_from_path

# === Functions ===
def extract_text(pdf_path):
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        
        # Initialize the list to store text from pages, skipping first and last pages
        pages_text = []
        
        # Loop through the pages, excluding the first and last pages
        for page_number in range(1, total_pages - 1):  # Skipping first (index 0) and last (index -1)
            page = doc.load_page(page_number)
            pages_text.append(page.get_text())

    return "\n".join(pages_text)

def extract_text_ocr(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        
        # Skip first and last page in the images list
        ocr_pages = [pytesseract.image_to_string(image) for image in images[1:-1]]  # Skipping first and last
        
        return "\n".join(ocr_pages)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return ""

def is_pdf_image_based(pdf_path):
    texts = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text()
            texts.append(text)
        combined_text = " ".join(texts)
        if len(combined_text) > 1500:
            #print(f"{pdf_path.name}: text-based")
            return False
        else:
            #print(f"{pdf_path.name}: image-based")
            return True

def clean_footer_line(line: str) -> str:
    """Normalize footer line (strip, single spaces, no digits-only)."""
    line = re.sub(r"\s+", " ", line).strip()
    if not line or line.isdigit():  # Ignore empty or digits-only lines
        return ""
    return line

def extract_common_footers(pdf_path: Path, threshold: float = 0.7) -> list[str]:
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        line_counts = defaultdict(int)

        for page in doc:
            rect = fitz.Rect(0, page.rect.height * 0.9, page.rect.width, page.rect.height)
            footer_text = page.get_text("text", clip=rect)
            lines = footer_text.split("\n")

            seen = set()
            for line in lines:
                clean = clean_footer_line(line)
                if clean and clean not in seen:
                    line_counts[clean] += 1
                    seen.add(clean)

        common_footers = [
            line for line, count in line_counts.items()
            if count / total_pages >= threshold
        ]

        return common_footers

def remove_footers_from_text(text: str, footers: list[str]) -> str:
    lines = text.split("\n")
    footer_set = set(footers)

    cleaned_lines = [line for line in lines if clean_footer_line(line) not in footer_set]
    return "\n".join(cleaned_lines)

def read_pdf(pdf_path):
    if is_pdf_image_based(pdf_path):
        return extract_text_ocr(pdf_path)
    else:
        return extract_text(pdf_path)

# === Run PDF Scrapping Full Pipeline ===
def run_pdf_scraping():
    # === Paths ===
    input_dir = Path("data/input_pdfs/test")
    output_dir = Path("data/extracted_text/clean_text")
    output_chunks_dir = Path("data/extracted_text/chunks") 
    output_dir.mkdir(parents=True, exist_ok=True)
    output_chunks_dir.mkdir(parents=True, exist_ok=True)  

    # === Main PDF Loop ===
    for pdf_file in input_dir.glob("*.pdf"):
        base_name = pdf_file.stem
        text = read_pdf(pdf_file)  

        # === Remove Footers ===
        common_footers = extract_common_footers(pdf_file)  # Detect common footers
        cleaned_text = remove_footers_from_text(text, common_footers)  # Remove footers from text

        # TOC detection code retained but disabled
        toc_found = False  # Force TOC as not found so font-size-based chunking is triggered

        # === Keep TOC detection code for future use ===
        # with fitz.open(pdf_file) as doc:
        #     total_pages = min(5, len(doc))
        #     for page_number in range(total_pages):
        #         page = doc.load_page(page_number)
        #         if table_of_contents.is_toc_page(page):
        #             toc_found = True
        #             break

        # Always run font-size-based chunking
        print(f"Extracting sections based on font size from {pdf_file.name}.")
        sections = chunking.extract_sections_from_text(cleaned_text)
        chunk_file_path = output_chunks_dir / f"{base_name}_chunks.txt"
        chunking.save_sections_to_file(sections, chunk_file_path)

        # === Outputs ===
        output_path = output_dir / f"{base_name}.txt"
        output_path.write_text(cleaned_text, encoding="utf-8")


