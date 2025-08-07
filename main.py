# DSSG_ERA/main.py 

# from web_scraper.run_scraper import run_scraper
# from classifier.run_classifier import run_classifier
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from risk_analysis.run_risk_analysis import pdfs_risk_analysis

# async def web_main():
#   """
#   Main entry point to initialize and run web-scraping pipeline, integrated with classification model
#   """
  
#   url_filepath = "data/inputs/websites/urls.json"
  
#   print("Starting web-scraping...")
#   await run_scraper(url_filepath)
  
#   print("Finished scraping. Starting classification...")
#   run_classifier()
  
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

    pdfs_risk_analysis(client, folder_path, "processed_files.txt", "file_input", 1)


if __name__ == "__main__":
    # asyncio.run(web_main())
    pdf_main()