import fitz
from pdf2image import convert_from_path
import pytesseract

def extract_image(path: str,remove_first: int = 0,remove_last: int = 0, 
                  dpi: int = 300,lang: str = 'eng') -> str:
    """
    Args:
        path: Path to the PDF file.
        dpi: Resolution for converting PDF pages to images.
        lang: Language(s) for Tesseract OCR.

    Returns:
        The combined OCR text of the selected pages, separated by blank lines.
    """
    doc = fitz.open(path)
    total = doc.page_count
    print(f"Loaded {total} pages.")
    doc.close()

    start_page = remove_first + 1
    end_page = total - remove_last
    # Convert only the specified page range to images

    pages = convert_from_path(path, dpi=dpi, first_page=start_page,last_page=end_page)
    print(f"Converted pages {start_page} to {end_page} to images.")

    if start_page > end_page:
        return ""
    
    full_text = []
    for idx, page_image in enumerate(pages, start=start_page):
        text = pytesseract.image_to_string(page_image, lang=lang)
        print(f"OCR page {idx}: {len(text)} chars")
        full_text.append(text)

    # Combine into one string
    ocr_result = "\n\n".join(full_text)
    return ocr_result

