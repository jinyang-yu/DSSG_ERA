import os
import json
import csv
import openai

# === Configuration ===

EXTRACTED_TEXT_DIR = "project/extracted_text/"
EVALUATION_DIR = "project/evaluation/"
RUNS_TO_EVALUATE = range(1, 11)  # Evaluates run1 through run10
MODEL = "gpt-4o"
MAX_CHARS = 5000

# === OpenAI Setup ===
#client = openai.OpenAI()# New SDK client instance

# === Utility Functions ===

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
You are evaluating a generated summary for factual faithfulness.

Below is a source report and a summary of it. Please assess whether the summary faithfully represents the source.

Respond with:
- A verdict: 'Faithful', 'Somewhat Faithful', or 'Not Faithful'
- A short justification (2-3 sentences)
- Optionally list any important missing or hallucinated details

--- Source Report ---
{source_text[:MAX_CHARS]}

--- Generated Summary ---
{summary_text}

Your evaluation:
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a detail-oriented evaluator of factual consistency."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return None

# === Main Evaluation Runner ===

def run_multiple_times():
    text_files = [f for f in os.listdir(EXTRACTED_TEXT_DIR) if f.endswith(".txt")]
    print(f"🔍 Found {len(text_files)} extracted source reports")

    for txt_file in text_files:
        # Strip "_text" from file name to match JSON output folder
        pdf_name = os.path.splitext(txt_file)[0].replace("_text", "")
        source_path = os.path.join(EXTRACTED_TEXT_DIR, txt_file)

        if not os.path.exists(source_path):
            print(f"⚠️ Skipping {pdf_name} — source text missing.")
            continue

        source_text = load_text_file(source_path)

        for run in RUNS_TO_EVALUATE:
            summary_path = os.path.join(EVALUATION_DIR, pdf_name, f"{pdf_name}_run{run}.json")
            verdict_path = os.path.join(EVALUATION_DIR, pdf_name, f"llm_faithfulness_run{run}.txt")

            if not os.path.exists(summary_path):
                print(f"⏭️ Skipping Run {run} for {pdf_name} — summary file not found.")
                continue

            print(f"🧠 Judging {pdf_name} (Run {run})")
            summary_text = load_summary_json(summary_path)

            verdict = judge_faithfulness(source_text, summary_text)

            if verdict:
                os.makedirs(os.path.dirname(verdict_path), exist_ok=True)
                with open(verdict_path, "w", encoding="utf-8") as f:
                    f.write(verdict)
                print(f"✅ Verdict saved to {verdict_path}")
            else:
                print(f"❌ Failed to get verdict for {pdf_name} Run {run}")

if __name__ == "__main__":
    run_multiple_times()
