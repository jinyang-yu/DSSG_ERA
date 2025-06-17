import spacy
nlp = spacy.load("en_core_web_sm")
sentences = [sent.text for sent in nlp(clean_text).sents]

#########################
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

def tok_len(s: str) -> int:
    return len(tokenizer.encode(s, add_special_tokens=False))

chunks = []
current_chunk = []
current_len   = 0

max_tokens = 1000

for sent in sentences:
    L = tok_len(sent)
    if L > max_tokens:
        # flush any partial chunk we were building
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0

        # (a) If a *single* sentence is already longer than max_tokens,
        #     break it into its own sub-chunks via a sliding window:
        ids = tokenizer.encode(sent, add_special_tokens=False)
        stride = max_tokens // 5  # or choose any overlap you like
        start = 0
        while start < len(ids):
            part = ids[start : start + max_tokens]
            chunks.append(tokenizer.decode(part, clean_up_tokenization_spaces=True))
            start += stride

        continue

    # (b) Otherwise, if adding this sentence would overflow:
    if current_len + L > max_tokens:
        chunks.append(" ".join(current_chunk))
        current_chunk = [sent]
        current_len   = L
    else:
        current_chunk.append(sent)
        current_len   += L

# (c) Finally, append any leftover
if current_chunk:
    chunks.append(" ".join(current_chunk))

with open("chunks_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(chunks))
print("\nChunks have been saved to 'chunks_output.txt'")