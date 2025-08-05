import json
import os
import torch
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# === Paths ===
risk_file = Path("data/risk_list.csv")
summary_logs_dir = Path("data/websites/with_summary")
output_path = Path("data/risk_website_pairs")
output_path.mkdir(parents=True, exist_ok=True)
output_file = output_path / "risk_website_pairs.json"

# === Model Config ===
model = SentenceTransformer('sentence-t5-base')

# === Functions ===
def load_risk_descriptions(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["Risk Description"])
    df["Risk Description"] = df["Risk Description"].astype(str).str.strip()
    return df.to_dict(orient="records")  

def load_summaries(summary_logs_dir: Path):
    summaries = []
    summary_metadata = []

    for file in summary_logs_dir.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON file: {file.name}")
                continue

            if isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict) and "content" in entry and "url" in entry:
                        summaries.append(entry["content"])
                        summary_metadata.append({
                            "url": entry["url"],
                            "title": entry.get("title", ""),
                            "content": entry["content"],
                            "summary": entry["summary"]
                        })
            elif isinstance(data, dict) and "content" in data and "url" in data:
                summaries.append(data["content"])
                summary_metadata.append({
                    "url": data["url"],
                    "title": data.get("title", ""),
                    "content": data["content"]
                })

    return summaries, summary_metadata

def match_risks_to_summaries(risks, summaries, summary_metadata, model, threshold=0.80):
    # Encode all Risk Descriptions
    risk_descriptions = [risk["Risk Description"] for risk in risks]
    risk_embeddings = model.encode(risk_descriptions, convert_to_tensor=True)

    # Encode all summaries
    summary_embeddings = model.encode(summaries, convert_to_tensor=True)

    results = {}
    for idx, risk_embedding in enumerate(risk_embeddings):
        risk_name = risks[idx]["Risk Name"]
        cosine_scores = util.pytorch_cos_sim(risk_embedding, summary_embeddings)[0]

        # Find indices where similarity >= threshold
        matching_indices = (cosine_scores >= threshold).nonzero(as_tuple=True)[0]

        matches = []
        for i in matching_indices:
            score = float(cosine_scores[i])
            match_summary = summary_metadata[int(i)]
            matches.append({
                "url": match_summary["url"],
                "title": match_summary.get("title", ""),
                "content": match_summary["content"],
                "summary": match_summary["summary"],
                "similarity_score": score
            })

        if matches:
            # Sort matches by descending similarity
            results[risk_name] = sorted(matches, key=lambda x: x["similarity_score"], reverse=True)

    return results

# === Run Risk-Website Pairing Full Pipeline ===
def run_risk_website_matching():
    print("Loading risk descriptions...")
    risks = load_risk_descriptions(risk_file)

    if not risks:
        print("No risk descriptions found.")
        return

    print("Loading summaries...")
    summaries, summary_metadata = load_summaries(summary_logs_dir)

    if not summaries:
        print("No summaries found.")
        return

    print("Matching risk descriptions to summaries...")
    results = match_risks_to_summaries(risks, summaries, summary_metadata, model)

    print(f"Saving results to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results
