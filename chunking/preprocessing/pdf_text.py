import fitz  # PyMuPDF


def extract_text(pdf_path: str,remove_first: int = 0,remove_last: int = 0) -> str:
    """
    Args:
      pdf_path: path to the PDF file.
      remove_first: number of pages to skip at the start.
      remove_last: number of pages to skip at the end.

    Returns:
      Combined text of the remaining pages, with two line-breaks between pages.
      If no pages remain, returns an empty string.
    """
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    print(f"Loaded {total_pages} pages.")

    # Calculate start and end indices
    start_page = remove_first
    end_page = total_pages - remove_last
    print(f"Extracting pages {start_page} to {end_page}.")

    # If the slicing range is invalid, return empty
    if start_page >= end_page or start_page < 0 or remove_last < 0:
        doc.close()
        return ""

    texts = []
    for pg in range(start_page, end_page):
        page = doc.load_page(pg)
        text = page.get_text()
        texts.append(text)
        print(f"Page {pg}: {len(text)} chars")

    doc.close()
    return "\n\n".join(texts)
