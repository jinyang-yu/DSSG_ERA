import fitz

def extract_sections_by_font(pdf_path, size_threshold=None):
    """
    Splits a PDF into sections by detecting lines whose average font size
    exceeds size_threshold (or auto‐computed) as headings.
    Returns a list of (heading, section_text).
    """
    doc = fitz.open(pdf_path)

    # First pass: collect all span sizes to choose a threshold if None
    all_sizes = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0: continue
            for line in block["lines"]:
                for span in line["spans"]:
                    all_sizes.append(span["size"])
    if size_threshold is None:
        # e.g. consider anything in the top 10% of sizes a heading
        all_sizes.sort()
        cutoff_idx = int(len(all_sizes) * 0.9)
        size_threshold = all_sizes[cutoff_idx]

    sections = []
    current_heading = None
    current_text = []
    total_word_count = 0

    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0: continue
            # Compute the average span size for this block
            block_sizes = [span["size"] for line in block["lines"] for span in line["spans"]]
            avg_size = sum(block_sizes) / len(block_sizes)
            text = "\n".join("".join(span["text"] for span in line["spans"])
                             for line in block["lines"]).strip()
            
            if not text:
                continue

            if avg_size >= size_threshold:
                # flush previous section
                if current_heading or current_text:
                #     sections.append((current_heading or "UNTITLED", "\n".join(current_text)))
                    section_text = "\n".join(current_text)
                    word_count = len(section_text.split())
                    total_word_count += word_count
                    print(f"[Section] {current_heading or 'UNTITLED'} — {word_count} words")
                    sections.append((current_heading or "UNTITLED", section_text))
                    
                    current_heading = text
                    current_text = []
            else:
                current_text.append(text)

    # flush last
    # if current_heading or current_text:
    #     sections.append((current_heading or "UNTITLED", "\n".join(current_text)))
    if current_heading or current_text:
        section_text = "\n".join(current_text)
        word_count = len(section_text.split())
        total_word_count += word_count
        print(f"[Section] {current_heading or 'UNTITLED'} — {word_count} words")
        sections.append((current_heading or "UNTITLED", section_text))
    print(f"\n Total word count across all sections: {total_word_count:,} words")
    return sections

# Usage:
sections = extract_sections_by_font("./data/Healix_Risk_Radar 2024_Web.pdf")
# with open("h_heading_output.txt", "w", encoding="utf-8") as f:
#     for heading, body in sections:
#         # write the heading
#         f.write(f"=== {heading}\n")
#         # write the entire section body
#         f.write(body)
#         # separate sections by a blank line
#         f.write("\n\n")

# print("Text has been saved to 'h_heading_output.txt'")