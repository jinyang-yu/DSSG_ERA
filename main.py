# DSSG_ERA/main.py 
import asyncio
import warnings
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from web_scraper.run_scraper import run_scraper
from classifier.run_classifier import run_classifier
from risk_pairing.scripts.news_article_summarization import summarize_articles_from_json
from risk_pairing.scripts.link_websites_to_risks import run_risk_summary_matching
from risk_analysis.run_risk_analysis import pdfs_risk_analysis

# gets rid of some warnings
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error" 

async def web_main():
  """
  Main entry point to initialize and run web-scraping pipeline, integrated with classification model
  """
  # filepaths
  url_filepath = "data/inputs/websites/urls.json"
  
  json_input_folder = Path("classifier/output")
  output_folder = Path("risk_pairing/outputs/websites_with_summary")
    
  print("Starting web-scraping...")
  await run_scraper(url_filepath)
  
  print("Finished scraping. Starting classification...")
  run_classifier()
  
  print("Finished classifying. Starting article summarization...")
  summarize_articles_from_json(json_input_folder, output_folder)
  
  print("Starting risk linking...")
  run_risk_summary_matching()
  
  print("Completed and saved risk summary and event linking in data/results.")
  
def pdf_main():
    """
    Main entry point to initialize and run pdf pipeline
    """
    print("Beginning PDF risk extraction...")
    # risk_analysis_main
    # Load environment variables from .env file
    load_dotenv()

    ### creates an instance of the OpenAI client
    client = OpenAI()

    folder_path = 'data/inputs/pdfs'

    pdfs_risk_analysis(client, folder_path, "risk_analysis/processed_files.txt", "file_search", 2)


if __name__ == "__main__":
    print('Enter which part of the project you would like to run:')
    x = input()
    if str(x) == "web":
        asyncio.run(web_main())
    elif str(x) == "pdf":
        pdf_main()
    elif str(x) == "both":
      pdf_main()
      asyncio.run(web_main())
    else:
        print("Invalid input")