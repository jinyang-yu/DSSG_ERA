import spacy
nlp = spacy.load("en_core_web_sm")

with open("output.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

doc = nlp(raw_text)
sentences = [sent.text.strip() for sent in doc.sents]

with open("rsentences_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sentences))
print("\nSentences have been saved to 'rsentences_output.txt'")

#########################
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
# Compute a dense vector for each sentence
embeddings = model.encode(sentences, convert_to_tensor=True)

import torch
from torch.nn.functional import cosine_similarity

# Compute similarity between sentence i and i+1
sims = [
    float(cosine_similarity(embeddings[i], embeddings[i+1], dim=0))
    for i in range(len(embeddings)-1)
]

# Choose a threshold, e.g. 0.75 (tune as needed)
threshold = 0.75

# Keep track of chunk boundaries
breakpoints = [0]  # always start at sentence 0
for i, sim in enumerate(sims):
    if sim < threshold:
        breakpoints.append(i+1)
breakpoints.append(len(sentences))  # end boundary

chunks = []
for start, end in zip(breakpoints, breakpoints[1:]):
    chunk_text = " ".join(sentences[start:end])
    chunks.append(chunk_text)

# Inspect
for idx, c in enumerate(chunks, 1):
    print(f"Chunk {idx} ({end-start} sents):", c[:100], "…")

with open("semantic_chunks_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(chunks))
print("\nChunks have been saved to 'semantic_chunks_output.txt'")