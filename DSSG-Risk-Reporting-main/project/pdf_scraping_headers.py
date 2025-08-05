from pathlib import Path
import fitz  # PyMuPDF
import re
import string
from collections import Counter
import statistics

# === Paths ===
input_dir = Path("data/test")
output_dir = Path("project/extracted_text")
visualizations_dir = output_dir / "visualizations"
output_dir.mkdir(parents=True, exist_ok=True)
visualizations_dir.mkdir(parents=True, exist_ok=True)

# === Helper: Detect TOC page ===


def is_toc_page(text: str) -> bool:
    lines = text.splitlines()
    dot_lines = [line for line in lines if re.search(r"\.{3,}", line)]
    page_num_lines = [line for line in lines if re.search(r"\s\d{1,3}$", line)]
    toc_keywords = ["contents", "chapter", "section", "page"]
    text_lower = text.lower()

    return (
        len(dot_lines) > 5 or len(page_num_lines) > 5 or
        (any(keyword in text_lower for keyword in toc_keywords) and
         (len(dot_lines) > 2 or len(page_num_lines) > 2))
    )

# === Extract TOC headers (multi-line support, no hierarchy) ===


def extract_toc_headers(pdf_path: Path):
    toc_entries = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text()
            if not is_toc_page(text):
                continue

            lines = text.splitlines()
            buffer = ""
            for line in lines:
                line = line.strip()
                if re.search(r"\.{3,}\s*\d{1,3}$", line):
                    full_line = (buffer + " " +
                                 line).strip() if buffer else line
                    match = re.match(r"(\s*)(.+?)\.{3,}\s*\d{1,3}$", full_line)
                    if match:
                        header_text = match.group(2).strip()
                        if len(header_text.split()) >= 2:
                            toc_entries.append(header_text.lower())
                    buffer = ""
                else:
                    buffer += " " + line
            if toc_entries:
                break  # Use only first TOC page
    return toc_entries

# === Utility: Normalization and Overlap ===


def simple_normalize(s):
    return s.lower().translate(str.maketrans('', '', string.punctuation)).strip()


def word_overlap_score(toc_text, line_text):
    set_toc = set(simple_normalize(toc_text).split())
    set_line = set(simple_normalize(line_text).split())
    return len(set_toc & set_line) / len(set_toc) if set_toc else 0

# === Extract text with headers ===


def extract_with_pymupdf(pdf_path: Path):
    toc_entries = extract_toc_headers(pdf_path)
    output_sections = []

    with fitz.open(pdf_path) as doc:
        for page in doc:
            if page.number == 0:
                print(f"Skipping title page in {pdf_path.name}")
                continue
            text = page.get_text()
            if is_toc_page(text):
                print(
                    f"Skipping TOC page {page.number + 1} in {pdf_path.name}")
                continue

            blocks = page.get_text("dict")["blocks"]
            lines = []

            for block in blocks:
                for line in block.get("lines", []):
                    line_text = ""
                    max_font_size = 0
                    bold = False
                    for span in line.get("spans", []):
                        if span["text"].strip():
                            line_text += span["text"].strip() + " "
                            max_font_size = max(max_font_size, span["size"])
                            if span["flags"] in [2, 3]:
                                bold = True
                    line_text = line_text.strip()
                    if line_text:
                        lines.append((line_text, max_font_size, bold))

            font_sizes = [font_size for _, font_size, _ in lines]
            font_threshold = statistics.median(
                font_sizes) + 1.5 if font_sizes else 12

            current_header_type = None
            current_header_text = None
            current_body = []
            matched_tocs = set()

            for i, (line_text, font_size, bold) in enumerate(lines):
                is_header = False
                header_type = "HEADER"
                normalized = line_text.lower().strip()

                if toc_entries:
                    for toc_text in toc_entries:
                        if toc_text not in matched_tocs and word_overlap_score(toc_text, line_text) > 0.5:
                            matched_tocs.add(toc_text)
                            is_header = True
                            header_type = "HEADER"
                            print(
                                f"Matched TOC: '{toc_text}' with line: '{line_text}'")
                            break
                else:
                    if font_size > font_threshold and (bold or line_text.istitle()) and len(line_text.split()) >= 2:
                        if i + 1 < len(lines) and len(lines[i + 1][0].split()) >= 5:
                            is_header = True

                if any(skip in normalized for skip in ["www.", "membership", "join today", "executive"]):
                    is_header = False

                if is_header:
                    if current_header_text:
                        output_sections.append(
                            (current_header_type, current_header_text,
                             "\n".join(current_body).strip())
                        )
                    current_header_type = header_type
                    current_header_text = line_text
                    current_body = []
                else:
                    current_body.append(line_text)

            if current_header_text:
                output_sections.append(
                    (current_header_type, current_header_text,
                     "\n".join(current_body).strip())
                )

    final_text = ""
    for header_type, header_text, body_text in output_sections:
        final_text += f"\n==={header_type}=== {header_text}\n\n"
        if body_text:
            final_text += body_text + "\n\n"
    return final_text

# === Extract visualizations ===


def extract_vector_visualizations(pdf_path: Path, save_dir: Path):
    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text().lower()
            if is_toc_page(text):
                print(f"Skipping TOC page {page_number} in {pdf_path.name}")
                continue

            exclusion_keywords = [
                "ceo", "president", "executive", "contact", "support", "office", "enquiries", "head office"
            ]
            if any(keyword in text for keyword in exclusion_keywords):
                print(f"Skipping profile/marketing page {page_number}")
                continue

            drawings = page.get_drawings()
            if len(drawings) < 8:
                continue

            numeric_matches = re.findall(r"\d{2,}|\d+[%$]", text)
            if len(numeric_matches) < 5:
                continue

            images = page.get_images(full=True)
            if len(images) > 2:
                continue

            inclusion_keywords = [
                "chart", "graph", "data", "percent", "risk",
                "trend", "table", "insight", "metric", "score"
            ]
            if not any(word in text for word in inclusion_keywords) and len(numeric_matches) < 8:
                continue

            try:
                pix = page.get_pixmap(dpi=300)
                image_path = save_dir / \
                    f"{pdf_path.stem}_page{page_number}_vector_full.png"
                pix.save(image_path)
                print(
                    f"Saved visualization from page {page_number}: {image_path.name}")
            except Exception as e:
                print(
                    f"Failed to save vector image for page {page_number}: {e}")


# === Main loop ===
for pdf_file in input_dir.glob("*.pdf"):
    base_name = pdf_file.stem
    print(f"\nProcessing: {pdf_file.name}")

    # Extract text with NLP headers
    pymupdf_text = extract_with_pymupdf(pdf_file)
    pymupdf_output_path = output_dir / f"{base_name}_text.txt"
    pymupdf_output_path.write_text(pymupdf_text, encoding="utf-8")

    # Extract visualizations
    extract_vector_visualizations(pdf_file, visualizations_dir)
