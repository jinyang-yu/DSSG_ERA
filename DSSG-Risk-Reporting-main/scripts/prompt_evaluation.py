import os
import json
import csv
from evaluation.models import o3_mini 
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from evaluation.models.o3_mini import risk_analysis_single_prompt
from evaluation.models.o3_mini import risk_analysis_all_prompts

# === OpenAI Setup ===
load_dotenv()

# === Paths ===
TEXT_FILES_DIR = "data/extracted_text/clean_text/test"
NUM_RUNS = 3
OUTPUT_BASE_DIR = "evaluation/outputs/"
TEXTS = [f for f in os.listdir(TEXT_FILES_DIR) if f.endswith(".txt")]

# === Functions ===
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_text_from_json(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Warning: File is missing or empty — {file_path}")
        return ""

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON — {file_path}")
        return ""

    risks_data = []
    if isinstance(data, dict):
        if "risks" in data:
            inner = data["risks"]
            if isinstance(inner, dict) and "risks" in inner and isinstance(inner["risks"], list):
                risks_data = inner["risks"]
            elif isinstance(inner, list):
                risks_data = inner
    elif isinstance(data, list):
        risks_data = data

    # Extract textual content
    risk_texts = []
    for item in risks_data:
        if isinstance(item, dict):
            risk_texts.append(" ".join(str(v) for v in item.values() if isinstance(v, str)))
        elif isinstance(item, str):
            risk_texts.append(item)

    return " ".join(risk_texts)

def compute_cosine_similarity(texts):
    valid_texts = [t for t in texts if isinstance(t, str) and len(t.strip()) > 10]

    if len(valid_texts) < 2:
        raise ValueError("Not enough valid texts to compute similarity.")

    model = SentenceTransformer('all-distilroberta-v1')  
    embeddings = model.encode(valid_texts, convert_to_tensor=False)  
    return cosine_similarity(embeddings)

def mean_similarity(sim_matrix):
    n = len(sim_matrix)
    total = 0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += sim_matrix[i][j]
            count += 1
    return total / count if count > 0 else 0

def print_similarity_matrix(pdf_name, texts, output_dir, prefix="run"):
    sim_matrix = compute_cosine_similarity(texts)
    print(f"Cosine Similarity Matrix for {pdf_name}:")

    for i in range(len(sim_matrix)):
        row = ["{:.2f}".format(score) for score in sim_matrix[i]]
        print(f"{prefix.capitalize()} {i+1}: {row}")

    csv_file_path = os.path.join(output_dir, f"{pdf_name}_similarity_matrix.csv")
    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        header = [prefix.capitalize()] + [f"{prefix.capitalize()} {i+1}" for i in range(len(sim_matrix))]
        writer.writerow(header)
        for i, row in enumerate(sim_matrix):
            writer.writerow([f"{prefix.capitalize()} {i+1}"] + ["{:.4f}".format(score) for score in row])
    print(f"Saved similarity matrix CSV to {csv_file_path}")

    mean_sim = mean_similarity(sim_matrix)
    print(f"Mean Cosine Similarity: {mean_sim:.4f}")
    return mean_sim

# === RUN PROMPT CONSISTENCY: SAME PROMPT MULTIPLE TIMES PIPELINE ===
def run_prompt_consistency():
    print("Extracted Text Files found:", TEXTS)

    summary = []

    for text in TEXTS:
        text_name = os.path.splitext(text)[0]
        text_dir = os.path.join(OUTPUT_BASE_DIR, "prompt_consistency", text_name)
        ensure_dir(text_dir)
        run_texts = []

        for run in range(1, NUM_RUNS + 1):
            output_file = os.path.join(text_dir, f"{text_name}_run{run}.json")

            if not os.path.exists(output_file):
                print(f"Processing {text} (Run {run})")
                result = risk_analysis_single_prompt(
                    open(os.path.join(TEXT_FILES_DIR, text)).read()
                )
                if result:
                    parsed_result = result[0] if isinstance(result, list) and len(result) > 0 else result

                    with open(output_file, 'w') as f:
                        json.dump(parsed_result, f, indent=2)

                    run_texts.append(load_text_from_json(output_file))
                else:
                    print(f"No result returned for {text} in run {run}")
                    run_texts.append("")
            else:
                print(f"Skipped {text} (already exists for run {run})")
                run_texts.append(load_text_from_json(output_file))

        try:
            mean_sim = print_similarity_matrix(text_name, run_texts, text_dir, prefix="run")
            summary.append((text_name, mean_sim))
        except ValueError as e:
            print(f"Skipping {text_name}: {e}")
            continue

    csv_path = os.path.join(OUTPUT_BASE_DIR, "prompt_consistency", "prompt_consistency_summary.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["PDF Name", "Mean Cosine Similarity"])
        for row in summary:
            writer.writerow([row[0], f"{row[1]:.4f}"])

    print(f"Summary CSV saved to {csv_path}")

# === RUN PROMPT SENSITIVITY: SAME TEXT, DIFFERENT PROMPTS PIPELINE ===
def run_prompt_sensitivity():
    print("Extracted Text Files found:", TEXTS)
    summary = []

    for text_file in TEXTS:
        text_name = os.path.splitext(text_file)[0]
        text_path = os.path.join(TEXT_FILES_DIR, text_file)
        text_dir = os.path.join(OUTPUT_BASE_DIR, "prompt_sensitivity", text_name)
        ensure_dir(text_dir)

        with open(text_path, 'r') as f:
            input_text = f.read()

        print(f"Running prompt sensitivity for {text_name}...")
        results = risk_analysis_all_prompts(
            input_text,
            override_output_dir=text_dir,
            ignore_if_exists=True
        )

        prompt_texts = []
        for i, result in enumerate(results):
            output_file = os.path.join(text_dir, f"prompt_{i+1}.json")
            prompt_texts.append(load_text_from_json(output_file))

        mean_sim = print_similarity_matrix(text_name, prompt_texts, text_dir, prefix="prompt")
        summary.append((text_name, mean_sim))

    summary_path = os.path.join(OUTPUT_BASE_DIR, "prompt_sensitivity", "prompt_sensitivity_summary.csv")
    with open(summary_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["PDF Name", "Mean Cosine Similarity Across Prompts"])
        for row in summary:
            writer.writerow([row[0], f"{row[1]:.4f}"])
    print(f"Saved sensitivity summary to {summary_path}")
