import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# === Paths ===
risk_folder = Path("risk_analysis/output")
summary_folder = Path("risk_pairing/outputs/websites_with_summary")
output_folder = Path("results")
output_folder.mkdir(parents=True, exist_ok=True)

# === Model Config ===
model = SentenceTransformer("sentence-t5-base")

# === Load Risks ===
def load_risk_descriptions_from_json_folder(risk_folder: Path):
    all_risks_by_file = {}

    for file in risk_folder.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "risks" in data and isinstance(data["risks"], list):
                    all_risks_by_file[file.name] = data["risks"]
                else:
                    print(f"⚠️ Skipping {file.name}: No 'risks' list found")
        except Exception as e:
            print(f"Failed to load {file.name}: {e}")
    return all_risks_by_file

# === Load Summaries ===
def load_summaries(summary_folder: Path):
    summaries = []
    summary_metadata = []

    for file in summary_folder.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Skipping invalid JSON file: {file.name}")
                continue

            for entry in data:
                if isinstance(entry, dict) and "summary" in entry and "url" in entry:
                    summaries.append(entry["summary"])
                    summary_metadata.append({
                        "url": entry["url"],
                        "title": entry.get("title", ""),
                        "summary": entry["summary"]
                    })

    return summaries, summary_metadata

# === Matching ===
def match_risks_to_summaries(risks, summaries, summary_metadata, threshold=0.80, max_matches=10):
    risk_descriptions = [r["risk_description"] for r in risks]
    risk_embeddings = model.encode(risk_descriptions, convert_to_tensor=True)
    summary_embeddings = model.encode(summaries, convert_to_tensor=True)

    for idx, risk in enumerate(risks):
        cosine_scores = util.pytorch_cos_sim(risk_embeddings[idx], summary_embeddings)[0]
        matches = []

        for i, score in enumerate(cosine_scores):
            if score >= threshold:
                matches.append({
                    "url": summary_metadata[i]["url"],
                    "title": summary_metadata[i]["title"],
                    "summary": summary_metadata[i]["summary"],
                    "similarity_score": float(score)
                })

        # Sort descending and keep only top max_matches
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        risk["matched_articles"] = matches[:max_matches]

    return risks

# === Pipeline ===
def run_risk_summary_matching():
    print("Loading risks...")
    risks_by_file = load_risk_descriptions_from_json_folder(risk_folder)

    if not risks_by_file:
        print("No risk JSON files found.")
        return

    print("Loading summaries...")
    summaries, summary_metadata = load_summaries(summary_folder)

    if not summaries:
        print("No summaries found.")
        return

    for filename, risks in risks_by_file.items():
        print(f"Matching risks in: {filename}")
        enriched_risks = match_risks_to_summaries(risks, summaries, summary_metadata, threshold=0.80)

        output_data = {"risks": enriched_risks}
        output_file = output_folder / filename

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Saved results to {output_file}")

# === Run ===
if __name__ == "__main__":
    run_risk_summary_matching()


