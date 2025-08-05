import fitz 
import re

def extract_sections_from_text(text, size_threshold=None, min_words=10, verbose=True):
    """
    Extracts sections from a plain text by detecting headings and capturing all text blocks
    until the next heading. Merges multi-line headings and handles structured sub-sections.
    """
    # Split the text into lines
    lines = text.splitlines()

    # Initialize variables
    sections = []
    current_heading = None
    current_text = []
    total_word_count = 0
    previous_was_heading = False

    for line in lines:
        line = line.strip()
        
        if not line:  # Skip empty lines
            continue

        # Detect headings (could be based on all caps or specific keywords)
        if line.isupper() or re.match(r"^[0-9]+\. ", line):  # Simple heading detection
            if previous_was_heading:
                # Append to previous heading if needed
                current_heading += " " + line
            else:
                # If there was a previous section, store it
                if current_heading or current_text:
                    section_text = "\n".join(current_text).strip()
                    word_count = len(section_text.split())
                    if word_count >= min_words:
                        sections.append((current_heading or "UNKNOWN_HEADING", section_text))
                        total_word_count += word_count
                        if verbose:
                            print(f"[CHUNK] {current_heading or 'UNKNOWN_HEADING'} — {word_count} words")
                # Start new heading
                current_heading = line
                current_text = []
            previous_was_heading = True
        else:
            # Collect regular text (part of a section)
            current_text.append(line)
            previous_was_heading = False

    # Final flush (if there was any remaining text)
    if current_heading or current_text:
        section_text = "\n".join(current_text).strip()
        word_count = len(section_text.split())
        if word_count >= min_words:
            sections.append((current_heading or "UNKNOWN_HEADING", section_text))
            total_word_count += word_count
            if verbose:
                print(f"[CHUNK] {current_heading or 'UNKNOWN_HEADING'} — {word_count} words")

    if verbose:
        print(f"\n[Total] Word count across all chunks: {total_word_count:,} words")

    return sections

def save_sections_to_file(sections, file_path, max_words=3500):
    """Helper function to save sections into a text file, splitting large sections into chunks."""
    with open(file_path, "w", encoding="utf-8") as f:
        for heading, section in sections:
            # Split the section into smaller chunks if it exceeds max_words
            chunks = split_chunk_into_parts(section, max_words)
            
            for chunk in chunks:
                f.write(f"[CHUNK] ({heading})\n{chunk}\n\n")
            
            # Print the final chunks for this section
            print(f"Final Chunks for '{heading}':")
            for i, chunk in enumerate(chunks, 1):
                print(f"  [Section {i}] {len(chunk.split())} words")


def split_chunk_into_parts(chunk, max_words=3500):
    """
    Splits a long chunk into smaller parts based on the maximum word limit.
    Default max_words is set to 1000 (can be adjusted).
    """
    words = chunk.split()  # Split the chunk into words
    parts = []
    part = ""
    word_count = 0  # Track word count to control splitting
    
    for word in words:
        # Add word to the current part if within the word limit
        if word_count + len(word.split()) <= max_words:
            part += word + " "
            word_count += len(word.split())  # Add the word's length to word_count
        else:
            # If the part is too long, add it to the list and start a new one
            parts.append(part.strip())  # Strip any extra spaces at the end
            part = word + " "
            word_count = len(word.split())  # Start count with the new word
    
    # Add the last part if there is any remaining text
    if part:
        parts.append(part.strip())
    
    return parts


