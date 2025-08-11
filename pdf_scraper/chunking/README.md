# DSSG_ERA_Chunking
Here are four ways of chunking that we implemented during exploration. Chunking is not embedded in our current
workflow but the scripts are kept here for your reference.
## 1. Fixed-size sliding window
- Divide text into blocks of fixed length (e.g., 3,000 tokens) with optional overlap (e.g., advance 1,000 tokens per chunk)
- Strengths: Generates more data; helps process long documents that exceed the input token limit
## 2. Heading-based splits
- Use document headings (e.g., section titles) to determine chunk boundaries
- Preserves logical structure
## 3. Sentence boundaries
- Use sentence tokenization to split at full sentence boundaries
- Preserves readability; simple, but not always optimal
## 4. Semantic chunking
- Group text using embeddings or similarity scores to keep related ideas together
- Preserves context across chunks; more complex to implement
