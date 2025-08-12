# Evaluation 
This folder contains the files to run evaluation on model output using an LLM-as-a-judge approach. Each report will output a file with a ranking of 1 (i.e., worst) - 5 (i.e., best) for factual faithfulness. 

## Folder Structure 
```
├── outputs/                        # Stores outputs from evaluation
│   ├── LLM_as_a_judge/             # Outputs from LLM-as-a-judge evaluation
│
├── scripts/                        # Evaluation scripts
│   ├── llm_as_judge.py             # Script for llm-as-a-judge
|evaluation_main.py                 # Main evaluation python file to run evaluation    
```

## Workflow
1. Gathers text files from pdf_scraper/outputs. This acts as the ground truth by which GPT-generated risk reports are compared to. 
2. Gathers json files from risk_analysis/output/file_search_txt_2. 
3. For each report, the text file and risk-related json file is fed to gpt-4 with a prompt asking for a         ranking of 1-5 based on factual faithfulness:
  - 1: The json summary file is completely unfaithful: there are more than 7 risks and/or related features      (e.g., description, drivers, trends, etc.) that are not present in the raw text file
  - 2: The json summary file is somewhat unfaithful: there are 5-6 risks and/or related features (e.g.,           description, drivers, trends, etc.) that are not present in the raw text file
  - 3: The json summary file is somewhat faithful: there are 3-4 risks and/or related features (e.g.,             description, drivers, trends, etc.) that are not present in the raw text file
  - 4: The json summary file is mostly faithful: there is 1-2 risk and/or related feature (e.g., description,     drivers, trends, etc.) that is not present in the raw text file
  - 5: The json summary file is completely faithful: all risks and their related features (e.g., description,     drivers, trends, etc.) are presented in the raw text file
4. Outputs a text file with the following information about that report:
  - A verdict: 'Completely Faithful', 'Mostly Faithful', 'Somewhat Faithful', 'Somewhat Unfaithful', or '         Completely Unfaithful'
  - Ranking of Faithfulness from 1-5
  - A short justification (2-3 sentences)

## Key Considerations 
- The current set-up assumes that risk-analysis json files are saved in 'risk_analysis/output/file_search_txt_2'. If this needs to be changed to other methods of risk extraction, please complete the following:
  - In evaluation_main.py, change line 9:
    input__risks_folder = root_io_path + "/risk_analysis/output/file_search_txt_2/test" #specifically  change         file_search_txt_2 to, e.g., file_input_2 
  - In llm_as_judge.py, change line 94:
    summary_filename = f"{base_name}_file_search_txt_2.json" ##specifically change file_search_txt_2 to,e.g., file_input_txt_2 






