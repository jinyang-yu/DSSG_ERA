import fitz  # pip install pymupdf

def chunk_by_page_fitz(pdf_path: str) -> list[str]:
    doc = fitz.open(pdf_path)
    return [page.get_text("text") for page in doc]

# Usage
page_chunks = chunk_by_page_fitz("./data/Healix_Risk_Radar 2024_Web.pdf")
for i, chunk in enumerate(page_chunks, 1):
    print(f"Page {i}: ~{len(chunk.split())} words")

with open("h_page_chunks_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(page_chunks))
print("\nPage chunks have been saved to 'h_page_chunks_output.txt'")