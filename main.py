# DSSG_ERA/main.py 

from web_scraper.run_scraper import run_scraper
from classifier.run_classifier import run_classifier
<<<<<<< HEAD
import asyncio
# from risk_analysis import risk_analysis_main
=======
from risk_analysis.run_risk_analysis import pdfs_risk_analysis
from dotenv import load_dotenv
from openai import OpenAI
>>>>>>> 86fed49 (update main)

async def web_main():
  """
  Main entry point to initialize and run web-scraping pipeline, integrated with classification model
  """
  
  url_filepath = "data/inputs/websites/urls.json"
  
  print("Starting web-scraping...")
  await run_scraper(url_filepath)
  
  print("Finished scraping. Starting classification...")
  run_classifier()
  
def pdf_main():
  """
  Main entry point to initialize and run pdf pipeline
  """
<<<<<<< HEAD
  print("Beginning PDF risk extraction...")
  # risk_analysis_main
=======
    # Load environment variables from .env file
    load_dotenv()

    ### creates an instance of the OpenAI client
    client = OpenAI()

    ### importing developer instructions
    instructions_path = 'risk_analysis/instructions.txt'
    with open(instructions_path, 'r', encoding='utf-8') as f:
        dev_instructions = f.read()

    pdfs_risk_analysis()
>>>>>>> 86fed49 (update main)
  
if __name__ == "__main__":
    asyncio.run(web_main())