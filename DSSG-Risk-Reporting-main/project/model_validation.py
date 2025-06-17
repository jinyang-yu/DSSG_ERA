# === SET UP ===

import os
import json
import csv
from project.risks import analyze_pdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai

# === Prompt Consistency Test ===

PDFS_DIR = "data/test/"
NUM_RUNS = 10
OUTPUT_BASE_DIR = "project/evaluation/"
PDFS = [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_text_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and "risks" in data:
        risks = data["risks"]
        # If it's a list of dicts, extract string content
        if isinstance(risks, list):
            risk_texts = []
            for item in risks:
                if isinstance(item, dict):
                    risk_texts.append(" ".join(str(v) for v in item.values() if isinstance(v, str)))
                elif isinstance(item, str):
                    risk_texts.append(item)
            return " ".join(risk_texts)
        elif isinstance(risks, str):
            return risks
    return ""

def compute_cosine_similarity(texts):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    return cosine_similarity(tfidf_matrix)

def mean_similarity(sim_matrix):
    n = len(sim_matrix)
    total = 0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):  # upper triangle, no diagonal
            total += sim_matrix[i][j]
            count += 1
    return total / count if count > 0 else 0

def print_similarity_matrix(pdf_name, texts):
    sim_matrix = compute_cosine_similarity(texts)
    print(f"\n📊 Cosine Similarity Matrix for {pdf_name}:")
    for i in range(len(sim_matrix)):
        row = ["{:.2f}".format(score) for score in sim_matrix[i]]
        print(f"Run {i+1}: {row}")

    mean_sim = mean_similarity(sim_matrix)
    print(f"\n📈 Mean Cosine Similarity (excluding self-similarity and duplicates): {mean_sim:.4f}")
    return mean_sim  # return value for CSV saving

def run_multiple_times():
    print("📄 PDFs found:", PDFS)

    summary = []  # list of (pdf_name, mean_similarity) for CSV

    for pdf in PDFS:
        pdf_name = os.path.splitext(pdf)[0]
        pdf_dir = os.path.join(OUTPUT_BASE_DIR, pdf_name)
        ensure_dir(pdf_dir)
        run_texts = []

        for run in range(1, NUM_RUNS + 1):
            output_file = os.path.join(pdf_dir, f"{pdf_name}_run{run}.json")

            if not os.path.exists(output_file):
                print(f"Processing {pdf} (Run {run})")
                result = analyze_pdf(pdf, override_output_dir=pdf_dir, ignore_analyzed=True)

                if result:
                    with open(output_file, 'w') as f:
                        json.dump(result, f)
                    print(f"✅ Saved output to {output_file}")
                    run_texts.append(load_text_from_json(output_file))
                else:
                    print(f"⚠️ No result returned for {pdf} in run {run}")
                    run_texts.append("")
            else:
                print(f"⏭️ Skipped {pdf} (already exists for run {run})")
                run_texts.append(load_text_from_json(output_file))

        mean_sim = print_similarity_matrix(pdf_name, run_texts)
        summary.append((pdf_name, mean_sim))

    # Save summary CSV
    csv_path = os.path.join(OUTPUT_BASE_DIR, "similarity_summary.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["PDF Name", "Mean Cosine Similarity"])
        for row in summary:
            writer.writerow([row[0], f"{row[1]:.4f}"])

    print(f"\n✅ Summary CSV saved to {csv_path}")

if __name__ == "__main__":
    run_multiple_times()

