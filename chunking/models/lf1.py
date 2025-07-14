import heading
from transformers import AutoTokenizer

# Load a tokenizer – use one similar to your Longformer model
tokenizer = AutoTokenizer.from_pretrained("allenai/longformer-base-4096")

sections = heading.extract_sections_by_font("chunking/data/124-WEF_The_Global_Risks_Report_2024.pdf")

### Heading Splitting
def preprocess_sections(sections, token_limit=3000, stride=1000):
    """
    Input:
      sections: list of (heading, text) tuples
      token_limit: max tokens per block
      stride: overlap when splitting large sections
    Output:
      processed_blocks: list of text blocks, each ≤ token_limit tokens
    """
    processed_blocks = []
    merge_bucket = []
    bucket_count = 0

    for heading, text in sections:
        block = f"{heading}\n{text}"
        tokens = tokenizer.encode(block, truncation=False)

        if len(tokens) > token_limit:
            # ── A) Flush any merged bucket first
            if merge_bucket:
                processed_blocks.append("\n\n".join(merge_bucket))
                merge_bucket, bucket_count = [], 0

            # ── B) Split this oversized section into sliding-window pieces
            print(f"[Split] '{heading}' ({len(tokens)} tokens) → splitting")
            for start in range(0, len(tokens), stride):
                piece_ids = tokens[start : start + token_limit]
                if not piece_ids:
                    break
                piece_text = tokenizer.decode(piece_ids, skip_special_tokens=True)
                processed_blocks.append(piece_text)
        else:
            # ── C) Try to merge into current bucket
            if bucket_count + len(tokens) <= token_limit:
                merge_bucket.append(block)
                bucket_count += len(tokens)
            else:
                # Flush full bucket, start a new one
                processed_blocks.append("\n\n".join(merge_bucket))
                merge_bucket = [block]
                bucket_count = len(tokens)

    # ── D) Flush any remaining merged bucket
    if merge_bucket:
        processed_blocks.append("\n\n".join(merge_bucket))

    return processed_blocks


chunks = chunk_sections_merge_split_slide(sections, token_limit=3000, stride=1000)

# Optional: Save chunks to disk
for i, chunk in enumerate(chunks):
    print(f"\n[Token count: {len(tokenizer.encode(chunk, truncation=False))}]")
    with open(f"chunk_{i+120}.txt", "w", encoding="utf-8") as f:
        f.write(chunk)

# for i, chunk in enumerate(chunks):
#     print(f"\n--- Chunk {i+1} ---")
#     print(chunk[:1000])  # Print first 1000 characters for preview (optional)  
