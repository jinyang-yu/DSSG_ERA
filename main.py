# DSSG_ERA/main.py 

from web_scraper.run_scraper import run_scraper
from classifier.run_classifier import run_classifier
import asyncio
# from risk_analysis import risk_analysis_main

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
  print("Beginning PDF risk extraction...")
  # risk_analysis_main
  
if __name__ == "__main__":
    asyncio.run(web_main())