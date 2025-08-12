# DSSG_ERA_GPT_Risk_Analysis
The scripts are built according to two ways of input: file input and file search, and there is an overarching main script which is run_risk_analysis where you get to choose which pipeline you want to use.

## Folder Structure 
```
├── output/                         # Stores outputs from pdf risk analysis
│   ├── file_input_1/               # Outputs from file input 1 pass
│   ├── file_input_2/               # Outputs from file input 2 pass
│   ├── file_search_1/              # Outputs from file search 1 pass (taking pdf)
│   ├── file_search_2/              # Outputs from file search 2 pass (taking pdf)
│   ├── file_search_txt_1/          # Outputs from file search 1 pass (taking txt)
│   ├── file_search_txt_2/          # Outputs from file search 2 pass (taking txt)
│
├── scripts/                        # Evaluation scripts
│   ├── file_input.py               # Script for file input both 1 pass and 2 pass
│   ├── file_search.py              # Script for file search both 1 pass and 2 pass
│   ├── instructions.txt            # developer instructions
|run_risk_analysis.py               # Main python file to run risk analysis  
|processed_files.txt                # Track the pdfs that have been processed already  
```

## file input
- Consists of two functions: one for one-pass and the other for two-pass
- Each function takes 6 parameters:
    - a client object
    - file_id for the file you uploaded
    - developer role instructions
    - user role prompt
    - model you choose, default is gpt-4.1-mini
    - temperature, default is 0.0
- Both functions return a response from API

## file search
- Vectorization of the uploaded file, consists of three steps:
    - Create a vector store
    - add the uploaded file to the vector store
    - Start vectorization, wait until it is completed to run next thing
- Consists of two functions: one for one-pass and the other for two-pass
- Each function takes 6 parameters:
    - a client object
    - file_id for the file you uploaded
    - developer role instructions
    - user role prompt
    - model you choose, default is gpt-4.1-mini
    - temperature, default is 0.0
- Both functions return a response from API

### upload file
- a function that upload file and return the corresponding file_id
- is used in both file input and file search

## run_risk_analysis
- The main file for GPT risk analysis
- The function takes 6 parameters:
    - a client object
    - folder_path to the folder that stores the input, and the function will take the entire file folder and process them using a for loop
        - for pdf: 'data/inputs/pdfs'
        - for text file: 'pdf_scraper/outputs'
    - record_file is the file that records the file that you have processed so that the function won't run risk analysis over the same file more than once
    - method is the way of input, set to file_input by default
    - pass type is where you get to choose 1 pass or 2 pass, default is 1
- The result is saved in the risk_analysis/output
