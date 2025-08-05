# DSSG_ERA/main.py 

from web_scraper.run_scraper import run_scraper
from classifier.run_classifier import run_classifier

def web_main():
  """
  Main entry point to initialize and run web-scraping pipeline, integrated with classification model
  """
  
  url_filepath = "data/inputs/websites/urls.json"
  
  print("Starting web-scraping...")
  run_scraper(url_filepath)
  
  print("Finished scraping. Starting classification...")
  run_classifier()
  
def pdf_main():
  """
  Main entry point to initialize and run pdf pipeline
  """
  
  