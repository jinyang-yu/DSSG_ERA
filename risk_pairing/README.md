# Website Article and Risk Name and Description Pairing 
This folder contains the files to run (1) website article summarization and (2) linking risk descriptions to website article summaries using cosine similarity. Importantly, website article summaries are only linked to risk descriptions if (1) above 0.80 for cosine similarity and (2) if there are more than 10 articles with above 0.80, only the top ten are linked to each risk. 

## Folder Structure 
```
├── outputs/                                          # Stores outputs
│   ├── websites_with_summary/                        # Outputs website jsons with the summary key            |                        
├── scripts/                                          # Linking scripts
│   ├── link_websites_to_risks_topic_modelling.py     # Script for linking based on topic modelling (archived)
│   ├── link_websites_to_risks.py                     # Using cosine similarity to link websites to risks
│   ├── news_article_summarization.py                 # Summarizes website articles
|
├── risk_list.cvs                                     # List of risks from Risk Universe. Use in topic modelling
```

## Workflow
1. Gathers website json files from classifier/output. 
2. Uses news_article_summarization.py to summarize each article. This is done using a two part process where (1) extracts relevant sentences using BERT (extractive summarization), and then (2) summarizes the extracted chunk using BART (abstractive summarization). A json file per website is outputted in risk_pairing/outputs/websites_with_summary.
3. Uses link_websites_to_risks.py to link the website summaries to risk descriptions. Website summaires are from risk_pairing/outputs/websites_with_summary and risk descriptions are from risk_analysis/output/files_search_txt_2. Outputs a json with website article summaries are only linked to risk descriptions if (1) above 0.80 for cosine similarity and (2) if there are more than 10 articles with above 0.80, only the top ten are linked to each risk in the main results folder. 

## Key Considerations 
- The current set-up assumes that risk-analysis json files are saved in 'risk_analysis/output/file_search_2'. If this needs to be changed to other methods of risk extraction, please complete the following:
  - In link_websites_to_risks.py, change line 7:
    risk_folder = Path("risk_analysis/output/files_search_txt_2") #specifically change file_search_txt_2 to, e.g., file_input_2 







