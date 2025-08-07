import os
import json
import re
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from transformers import BartForConditionalGeneration, BartTokenizer

# === Paths ===
# JSON_FOLDER = Path("classifier/output")
# OUTPUT_FOLDER = Path("risk_pairing/outputs/websites_with_summary")
# OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# === Model Config ===
# Load the pre-trained BERT extractive summarization model (Sentence Transformer)
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the pre-trained BART model and tokenizer for abstractive summarization
model_name = "facebook/bart-large-cnn"
bart_model = BartForConditionalGeneration.from_pretrained(model_name)
bart_tokenizer = BartTokenizer.from_pretrained(model_name)

# === Functions ===
# Function to clean content by removing irrelevant sections (author, navigation, etc.)
def clean_content(clean_text):
    clean_text = re.sub(r"By [A-Za-z\s]+", "", clean_text)  
    clean_text = re.sub(r"\d{4}-\d{2}-\d{2}", "", clean_text)  
    clean_text = re.sub(r"http[s]?://\S+", "", clean_text)  
    clean_text = re.sub(r"(related articles?|more info|advertisement|sponsored)\s*.*", "", clean_text, flags=re.IGNORECASE)  # Remove navigation
    return clean_text.strip()

# Function to load JSON data
def load_json_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Function to compute the cosine similarities between sentences in the content
def compute_similarities(clean_text):
    sentences = clean_text.split(".")
    
    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Get embeddings for each sentence
    sentence_embeddings = bert_model.encode(sentences, convert_to_tensor=True)
    
    # Compute cosine similarities between sentences
    similarities = util.pytorch_cos_sim(sentence_embeddings, sentence_embeddings)
    
    return similarities

# Function to extract the most relevant sentences using BERT (extractive)
def extract_relevant_sentences(text, num_sentences=5):
    cleaned_content = clean_content(text)  # Clean the text before summarization
    similarities = compute_similarities(cleaned_content)  # Compute sentence similarities
    
    # Get the sentence scores 
    sentence_scores = similarities.mean(dim=1) 
    
    # Get the top `num_sentences` sentences based on their scores
    top_sentence_indices = sentence_scores.argsort(descending=True)[:num_sentences]  
    
    # Get the relevant chunk
    sentences = cleaned_content.split(".")
    relevant_chunk = [sentences[i].strip() for i in top_sentence_indices]
    
    return relevant_chunk

# Function to generate an abstractive summary using BART
def generate_bart_summary(text):
    inputs = bart_tokenizer([text], max_length=1024, return_tensors="pt", truncation=True, padding="longest")
    
    summary_ids = bart_model.generate(
        inputs["input_ids"],
        max_length=200,   
        min_length=50,    
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=2, 
        length_penalty=1.5, 
        top_p=0.95,         
        top_k=50         
    )
    
    summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Function to sanitize filenames (remove/replace invalid characters)
def sanitize_filename(url):
    return re.sub(r'[^\w\-_\. ]', '_', url)  

# === Run Article Summarization Full Pipeline ===
# Function to summarize articles and save them into a single JSON file per website
def summarize_articles_from_json(folder_path, output_folder):
    # Loop through each JSON file in the folder (each file corresponds to a website)
    output_folder.mkdir(parents=True, exist_ok=True)
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = folder_path / file_name
            articles_data = load_json_data(file_path)
            
            # Process each article in the JSON file
            for article in articles_data:
                url = article.get("url", "")
                clean_text = article.get("cleaned_text", "")
                
                if clean_text:
                    # Clean the content before processing
                    cleaned_content = clean_content(clean_text)
                    print(f"Processing article from URL: {url}")

                    # Step 1: Extract relevant sentences using BERT (extractive summarization)
                    relevant_chunk = extract_relevant_sentences(cleaned_content, num_sentences=5)
                    
                    if not relevant_chunk:
                        print(f"No relevant chunk extracted for URL: {url}")
                        continue  # Skip this article if no relevant sentences found
                    
                    # Step 2: Summarize the extracted chunk using BART (abstractive summarization)
                    summary = generate_bart_summary(" ".join(relevant_chunk))  # Join the sentences into a chunk
                    
                    # Add the summary to the article
                    article["summary"] = summary

                    # Print the summary for each URL
                    print(f"URL: {url}")
                    # print(f"Extracted Chunk: {' '.join(relevant_chunk)}")  # Optional
                    print(f"Summary: {summary}\n")
            
            # Save the modified data (with summaries) back to the JSON file for this website
            output_file = output_folder / file_name
            with open(output_file, "w") as f:
                json.dump(articles_data, f, indent=4)

if __name__ == "__main__":
    summarize_articles_from_json(JSON_FOLDER, OUTPUT_FOLDER)