# DSSG_ERA_GPT_Risk_Analysis
The scripts are built according to two ways of input: file input and file search, and there is an overarching main script which is run_risk_analysis where you get to choose which pipeline you want to use.

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
    - folder_path for the folder that stores the pdfs, and the function will take the entire file folder and process them using a for loop
    - record_file is the file that records the file that you have processed so that the function won't run risk analysis over the same file more than once
    - method is the way of input, set to file_input by default
    - pass type is where you get to choose 1 pass or 2 pass, default is 1
- The result is saved in the risk_analysis/output
