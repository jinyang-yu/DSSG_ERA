import os
import sys
import json
from pathlib import Path 
from scripts import llm_as_judge

def initialize_evaluated_file():
    """Initialize the evaluated.json file if it doesn't exist."""
    if not os.path.exists('evaluated.json'):
        with open('evaluated.json', 'w') as f:
            json.dump({"Evaluated": []}, f)
        print("Created evaluated.json file")

def run_evaluation(root_io_path):
    initialize_evaluated_file()

    input_folder = root_io_path + "/pdf_scraper/outputs/test"
    input__risks_folder = root_io_path + "/risk_analysis/output/file_search_2/test"
    output_base_dir = os.path.join(root_io_path, "evaluation", "outputs")

    print("Starting LLM as a Judge process...")
    llm_as_judge.run_llm_as_judge(
        text_files_dir=input_folder,
        input__risks_folder=input__risks_folder,
        output_folder=os.path.join(output_base_dir, "LLM_as_a_judge"))
    print("LLM as a Judge completed")

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
    run_evaluation(root_io_path=root_dir)

