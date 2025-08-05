#!/usr/bin/env python3

import os
import sys
import json

def initialize_analyzed_file():
    """Initialize the analyzed.json file if it doesn't exist."""
    if not os.path.exists('analyzed.json'):
        with open('analyzed.json', 'w') as f:
            json.dump({"Analyzed": []}, f)
        print("Created analyzed.json file")

def main():
    """Main entry point for the risk reporting tool."""
    # Add the project root directory to sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.append(project_root)

    # Ensure the analyzed.json file exists
    initialize_analyzed_file()

    # Ensure output directories exist
    directories = [
        'project/results/',
        'project/table_content/images/',
        'project/table_content/dictionaries/',
        'project/sections/pdf_sections/',
        'project/sections/combinations/',
        'project/evaluation/'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Import and run scripts

    #print("Starting Text Extraction process...")
    #from project import pdf_scraping  
    #print("Text Extraction completed")

    #print("Starting Prompt Consistency Evaluation process...")
    #from project import model_validation
    #model_validation.run_multiple_times()  
    #print("Prompt Consistency Evaluation completed")

    print("Starting LLM as a Judge Evaluation process...")
    from project import model_validation_llm_as_judge
    model_validation_llm_as_judge.run_multiple_times()  
    print("LLM as a Judge Evaluation completed")

if __name__ == "__main__":
    main()
