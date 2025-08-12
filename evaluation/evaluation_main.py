import os
import sys
import json
from pathlib import Path 
from scripts import llm_as_judge

def run_evaluation(root_io_path):
    input_folder = root_io_path + "/pdf_scraper/outputs/test"
    input__risks_folder = root_io_path + "/risk_analysis/output/file_search_txt_2/test"
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
