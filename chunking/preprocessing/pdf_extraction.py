import fitz  # PyMuPDF
import pdf_ocr
import pdf_text

def is_image_only_pdf(path, min_chars_per_page=600):
    """
    Returns True if EVERY page has fewer than `min_chars_per_page`
    of extractable text → likely a scanned/image-only PDF.
    """
    doc = fitz.open(path)
    for page in doc:
        text = page.get_text().strip()
        if len(text) >= min_chars_per_page:
            # Found enough text on at least one page
            doc.close()
            return False
    doc.close()
    return True


def extract_pdf(path, remove_first: int = 0, remove_last: int = 0):
    if is_image_only_pdf(path):
        return pdf_ocr.extract_image(path, remove_first, remove_last)
    else:
        return pdf_text.extract_text(path, remove_first, remove_last)
    

# Path to your PDF file
path = 'chunking/data/15-higher-education-sector-risk-profile-2023.pdf'
raw = extract_pdf(path)
with open('15raw.txt', 'w', encoding='utf-8') as f:
    f.write(raw)