# Data Science for Social Good - ERA Project

This repository outlines the 2025 DSSG project, partnered with the ERA team. 

The project streamlines the automated process for risk extraction on textual data (PDF reports & web articles). 

## Workflow Overview 
The high-level overview on the final product can be seen in the workflow diagram below. 
![Workflow Diagram](images/workflow_diagram.png)

## Table of Contents 
1. [Classifier](DSSG_ERA/classifier) : Classification Model for Web Articles
2. [Data](DSSG_ERA/data) : Input data and results files for the overarching pipeline
3. [Evaluation](DSSG_ERA/evaluation) : Model and prompt evaluation folders
4. [Images](DSSG_ERA/images) : Contains workflow diagram
5. [PDF Scraper](DSSG_ERA/pdf_scraper) : Includes contents of PDF preprocessing
6. [Risk Analysis](DSSG_ERA/risk_analysis) : Main folder for GPT risk analysis
7. [Risk Pairing](DSSG_ERA/risk_pairing) : Pairing of website risk events with extracted PDF risks
8. [Web Scraper](DSSG_ERA/web_scraper) : Website scraping tool

## Project Code Flow
- In reference to the `main.py` file, the general flow of our code structure goes as follows if you run **both** processes
- The diagram is separated by the two colors indicating what functions are triggered by each branch: web (green) and pdf (orange)


```mermaid
flowchart LR
        S([Start]) --> A[URLs]
        S --> F[PDFs]
        A --> B[Web Scraper] --> C[Classifier] --> D[Website Summarization]
        F--> G[GPT Risk Analysis]
        D --> E[Link Website Events with PDF Risk Analysis]
        G --> E
 %% Assign classes
    class S startNode;
    class A,B,C,D,E urlsPath;
    class F,G pdfsPath;
 %% Define styles
    classDef startNode fill:#a2d2ff,stroke:#333,stroke-width:2px;
    classDef urlsPath fill:#b7e4c7,stroke:#333,stroke-width:1px;
    classDef pdfsPath fill:#ffb480,stroke:#333,stroke-width:1px;
```


## Key Components 
### 1. Classification Model (`classifier/`)
- Main file to run classifier on website articles (`run_classifier.py`)
- Consists of two versions:
    - `scripts/gpt_main.py`: GPT classifier (base)
    - `scripts/catboost_main.py`: Catboost semi-supervised model (v2)
- `classified.json`: Tracking of files already classified
- `output/`: Output website files from classifier model
- Function: Joins all web-scraped files, cleans content through REGEX, feeds into classifier -> saves filtered content & its metadata
### 2. Evaluation (`evaluation/`)
- Runs scripts for LLM-as-a-judge, using GPT model as a proxy for a human evaluator (`evaluation_main.py`)
- `outputs/LLM_as_a_judge`: Output evaluation text file per pdf report
- Function: Run evaluation on the risk analysis model's output using an LLM-as-a-judge approach. Each report will output a file with a ranking of 1 (i.e., worst) - 5 (i.e., best) for factual faithfulness. 
  
### 3. GPT Risk Analysis (`risk_analysis/`)
- Initializes overall GPT risk analysis on PDF reports (`run_risk_analysis.py`)
- Contains two versions:
  - `file_input.py`: Analysis through file input
  - `file_search.py`: Analysis through file search
- `processed_files.txt`: Tracker for all processed reports
- `output/`: Risk analysis output, each subfolder contains the output for a specific input method and pass configuration. The folder names indicate both the input type (file input, file search) and the number of processing passes performed during the analysis. The naming convention follows this pattern:
    - File input 1: Results from file input processing with a single pass
    - File search txt 2: Results from text file search processing with 2 passes
- Function: Take the input folder for pdfs, iterate through the PDF folder using a for loop to identify all unprocessed PDF files. For each unprocessed PDF, execute the risk analysis using the specified method (file input, file search) and designated number of passes (1, 2).

### 4. Summarizing Website Articles (`risk_pairing/`)
- Summarizes each article content (`scripts/news_article_summarization.py`)
- `outputs/website_with_summary`: Output summarization json file per website
- Function: Summarizes website articles using a two part process where (1) extracts relevant sentences using BERT (extractive summarization), and then (2) summarizes the extracted chunk using BART (abstractive summarization).

### 5. Linking Web and PDF Content (`risk_pairing/`)
- Links website content to PDF extracted risks (`/scripts/link_websites_to_risks.py`) 
- `results`: Output of risk analysis plus linked website articles.
- Function: Uses cosine similarity to link risk descriptions to website summaries based on if (1) above 0.80 for cosine similarity and (2) if there are more than 10 articles with above 0.80, only the top ten are linked to each risk in the main results folder. 

### 6. Web-Scraping Tool (`web_scraper/`)
- Main running script to start web-scraping (`run_scraper.py`)
- Consists of two versions:
  - `scraper/website_scraper.py`: Uses BeautifulSoup + Playwright for dynamically rendered content (base)
  - `scraper/dynamic_web_scraper.py`: Implements loading buttons + pagination (v2)
- `output/urls/visited_urls.json`: Tracker for all visited URLS
- `output/raw_results/`: Results for all raw web-scraped content 
- Updates Google Sheets on Mckinsey PDF reports to manually check 
- Function: Takes input, extracts title, content, url & date -> saves file for each source per run

### 7. Data (`data/`)
- Input:
  - `inputs/pdfs`: All PDF reports to run
  - `inputs/text`: Text files of PDF reports
  - `inputs/websites/urls.json`: URL configuration for website branch
- Results: Extracted PDF risk files with linked website risk events

### 8. OpenAI models
- `classifier/model/chat4o_mini.py`: Uses **GPT 4o-mini model** to classify risk-relevant articles
- `evaluation/scripts/llm_as_judge.py`: **GPT 4** implemented for LLM-as-a-judge evaluation
- `risk_analysis/file_input.py`: Risk analysis through file input run on **GPT 4.1 mini** (default)
- `risk_analysis/file_search.py`: Risk analysis through file search run on **GPT 4.1 mini** (default)

## Installation Instructions 
1. Clone this repository
3. Create and activate a virtual environment
   - Currently configured for `Python 3.13`
   - Store .env file for OpenAI key in the root directory `dssg_era/`
4. Install dependencies from `requirements.txt`

## Usage Guide
1. Run `main.py`
2. Specify which branch of the workflow you'd like to run:
   - If you'd like to run the whole process -> type `both`
   - If you'd just like to run the website section + linkage -> type `web`
   - If you'd just like to run the PDF extraction -> type `pdf`
