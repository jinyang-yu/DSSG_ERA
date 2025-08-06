import re
import fitz
from difflib import SequenceMatcher

def is_toc_page(page) -> bool:
    toc_keywords = ["table of contents", "contents", "chapters", "sections", "index", "page", "summary"]
    page_dict = page.get_text("dict")

    # First, collect all font sizes
    font_sizes = []
    for block in page_dict.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                size = span.get("size")
                if size is not None:
                    font_sizes.append(size)

    if not font_sizes:
        return False

    max_font_size = max(font_sizes)

    # Now search for TOC keywords only in spans with the largest font
    for block in page_dict.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("size") == max_font_size:
                    span_text = span.get("text", "").strip().lower()
                    if any(keyword in span_text for keyword in toc_keywords):
                        return True

    return False
