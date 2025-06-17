from pathlib import Path
import fitz  # PyMuPDF
import pdfplumber
import re

# === Paths ===
input_dir = Path("data/test")
output_dir = Path("project/extracted_text")
visualizations_dir = output_dir / "visualizations"
output_dir.mkdir(parents=True, exist_ok=True)
visualizations_dir.mkdir(parents=True, exist_ok=True)

# === Text Extraction ===
def extract_with_pymupdf(pdf_path: Path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# === Helper to detect TOC pages ===
def is_toc_page(text: str) -> bool:
    # Heuristic 1: many lines with dots or repeated spaces near numbers (typical TOC layout)
    lines = text.splitlines()
    dot_lines = [line for line in lines if re.search(
        r"\.{3,}", line)]  # lines with 3+ dots

    # Heuristic 2: lines ending with a page number (number at end of line)
    page_num_lines = [line for line in lines if re.search(r"\s\d{1,3}$", line)]

    # Heuristic 3: If many such lines exist, assume TOC
    if len(dot_lines) > 5 or len(page_num_lines) > 5:
        return True

    # Also check for keywords commonly in TOCs
    toc_keywords = ["contents", "chapter", "section", "page"]
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in toc_keywords) and (len(dot_lines) > 2 or len(page_num_lines) > 2):
        return True

    return False

# === Vector Visualization Extraction with Heuristics ===
def extract_vector_visualizations(pdf_path: Path, save_dir: Path):
    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text().lower()

            # Skip Table of Contents
            if is_toc_page(text):
                print(f"Skipping TOC page {page_number} in {pdf_path.name}")
                continue

            # Exclude intro, corporate, or contact pages
            exclusion_keywords = [
                "ceo", "president", "executive", "introduction",
                "contact", "support", "office", "enquiries", "head office"
            ]
            if any(keyword in text for keyword in exclusion_keywords):
                print(f"Skipping profile/marketing page {page_number}")
                continue

            # Check for visual content
            drawings = page.get_drawings()
            if len(drawings) < 8:
                continue  # Need enough vector elements

            # Look for numeric indicators of data
            numeric_matches = re.findall(r"\d{2,}|\d+[%$]", text)
            if len(numeric_matches) < 5:
                continue  # Likely not quantitative data

            images = page.get_images(full=True)
            if len(images) > 2:
                continue  # Likely full-image layout or collage

            # Check for meaningful keywords
            inclusion_keywords = [
                "chart", "graph", "data", "percent", "risk",
                "trend", "table", "insight", "metric", "score"
            ]
            keyword_match = any(word in text for word in inclusion_keywords)

            # Allow visuals with good numeric density even without keywords
            if not keyword_match and len(numeric_matches) < 8:
                continue

            try:
                pix = page.get_pixmap(dpi=300)
                image_path = save_dir / f"{pdf_path.stem}_page{page_number}_vector_full.png"
                pix.save(image_path)
                print(f"Saved visualization from page {page_number}: {image_path.name}")
            except Exception as e:
                print(f"Failed to save vector image for page {page_number}: {e}")

# === Main PDF Loop ===
for pdf_file in input_dir.glob("*.pdf"):
    base_name = pdf_file.stem

    # Extract text
    pymupdf_text = extract_with_pymupdf(pdf_file)
    pymupdf_output_path = output_dir / f"{base_name}_pymupdf.txt"
    pymupdf_output_path.write_text(pymupdf_text, encoding="utf-8")

    # Extract only relevant vector-based visualizations
    extract_vector_visualizations(pdf_file, visualizations_dir)
