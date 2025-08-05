import os
import sys
import json
from pathlib import Path 
from scripts import pdf_scraping
from scripts import news_article_summarization
from scripts import link_websites_to_risks
from scripts import link_websites_to_risks_topic_modelling


def initialize_analyzed_file():
    """Initialize the analyzed.json file if it doesn't exist."""
    if not os.path.exists('analyzed.json'):
        with open('analyzed.json', 'w') as f:
            json.dump({"Analyzed": []}, f)
        print("Created analyzed.json file")

def main():
    """Main entry point for the risk reporting tool."""

    # Ensure the analyzed.json file exists
    initialize_analyzed_file()

    # Import and run 
    print("Starting PDF Scraping process...")
    pdf_scraping.run_pdf_scraping()
    print("PDF Scraping completed")

    #print("Starting Web Scraping process...")
    #ADD SCRIPT AND MAIN PIPELINE FUNCTION HERE
    #print("PDF Web completed")

    #print("Starting Risk Analysis process...")
    #ADD SCRIPT AND MAIN PIPELINE FUNCTION HERE
    #print("Risk Analysis completed")
 
    print("Starting News Article Summarization process...")
    news_article_summarization.run_news_article_summarization()
    print("News Article Summarization completed")

    print("Starting Risk Name and Website Article Linking process...")
    link_websites_to_risks.run_risk_website_matching()
    print("Risk Name and Website Article Linking completed")

    print("Starting Risk Name and Website Article Linking (Topic Modelling) process...")
    link_websites_to_risks_topic_modelling.run_risk_website_matching_tm()
    print("Risk Name and Website Article Linking (Topic Modelling) completed")

if __name__ == "__main__":
    main()