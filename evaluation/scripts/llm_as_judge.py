import os
import json
import openai
import re
from dotenv import load_dotenv

# === OpenAI Setup ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 

# === Model Config ===
MODEL = "gpt-4" 
temperature=0.3 
MAX_CHARS = 5000
RUNS_TO_EVALUATE = list(range(1, 2)) 

# === Functions ===
def texts_(text_files_dir):
    return [f for f in os.listdir(text_files_dir) if f.endswith(".txt")]

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
def load_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_summary_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "risks" in data:
        risks = data["risks"]
        texts = []
        for r in risks:
            if isinstance(r, dict):
                texts.append(" ".join(str(v) for v in r.values() if isinstance(v, str)))
            elif isinstance(r, str):
                texts.append(r)
        return "\n".join(texts)
    return ""

def judge_faithfulness(source_text, summary_text):
    prompt = f"""
You are evaluating a generated summary for factual faithfulness. You will be given the raw text file of a report 
and a json file that contains a summary of risk related information. 

Please assess whether the summary faithfully represents the text file source.

Give your answer as a float on a scale of 1 to 5 where: 
    1: The json summary file is completely unfaithful: there are more than 7 risks and/or related features (e.g., description, drivers, trends, etc.) that are not present in the raw text file
    2: The json summary file is somewhat unfaithful: there are 5-6 risks and/or related features (e.g., description, drivers, trends, etc.) that are not present in the raw text file
    3: The json summary file is somewhat faithful: there are 3-4 risks and/or related features (e.g., description, drivers, trends, etc.) that are not present in the raw text file
    4: The json summary file is mostly faithful: there is 1-2 risk and/or related feature (e.g., description, drivers, trends, etc.) that is not present in the raw text file
    5: The json summary file is completely faithful: all risks and their related features (e.g., description, drivers, trends, etc.) are presented in the raw text file

Respond with:
- A verdict: 'Completely Faithful', 'Mostly Faithful', 'Somewhat Faithful', 'Somewhat Unfaithful', or 'Completely Unfaithful'
- Ranking of Faithfulness from 1-5
- A short justification (2-3 sentences)

--- Source Report ---
{source_text[:MAX_CHARS]}

--- Generated Summary ---
{summary_text}

Your evaluation:
"""
    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a detail-oriented evaluator of factual consistency."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM call failed: {e}")
        return None

# === Run Main Pipeline Function ===
def run_llm_as_judge(text_files_dir, input__risks_folder, output_folder):
    text_files = [f for f in os.listdir(text_files_dir) if f.endswith(".txt")]
    print(f"Found {len(text_files)} extracted source reports")

    for txt_file in text_files:
        source_path = os.path.join(text_files_dir, txt_file)

        # Normalize the base name if needed (e.g., replace spaces with underscores)
        base_name = os.path.splitext(txt_file)[0].replace(" ", "_")
        summary_filename = f"{base_name}_file_search_2.json"
        summary_path = os.path.join(input__risks_folder, summary_filename)

        if not os.path.exists(source_path):
            print(f"Skipping {txt_file} — source text missing.")
            continue

        source_text = load_text_file(source_path)

        for run in RUNS_TO_EVALUATE:
            verdict_path = os.path.join(output_folder, os.path.splitext(txt_file)[0], f"llm_faithfulness_run{run}.txt")

            if not os.path.exists(summary_path):
                print(f"Looking for summary: {summary_path}")
                print(f"Skipping Run {run} for {txt_file} — summary file not found.")
                continue

            print(f"Judging {txt_file} (Run {run})")
            summary_text = load_summary_json(summary_path)

            verdict = judge_faithfulness(source_text, summary_text)

            if verdict:
                os.makedirs(os.path.dirname(verdict_path), exist_ok=True)
                with open(verdict_path, "w", encoding="utf-8") as f:
                    f.write(verdict)
                print(f"Verdict saved to {verdict_path}")
            else:
                print(f"Failed to get verdict for {txt_file} Run {run}")
