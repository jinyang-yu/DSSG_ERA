import os
import sys
import json
from pathlib import Path 
from scripts import prompt_evaluation
from scripts import llm_as_judge

def initialize_evaluated_file():
    """Initialize the evaluated.json file if it doesn't exist."""
    if not os.path.exists('evaluated.json'):
        with open('evaluated.json', 'w') as f:
            json.dump({"Evaluated": []}, f)
        print("Created evaluated.json file")

def main():
    """Main entry point for model evaluation."""

    # Ensure the evaluated.json file exists
    initialize_evaluated_file()

    # Import and run 
    print("Starting Prompt Consistency process...")
    prompt_evaluation.run_prompt_consistency()
    print("Prompt Consistency completed")

    print("Starting Prompt Sensitivity process...")
    prompt_evaluation.run_prompt_sensitivity()
    print("Prompt Sensitivity completed")

    print("Starting LLM as a Judge process...")
    llm_as_judge.run_llm_as_judge()
    print("LLM as a Judge completed")

if __name__ == "__main__":
    main()