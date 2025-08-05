# Web-Scraping Tool 
This folder contains the files to run the web-scraping tool, of 11 different URLs and saves the extracted content. 

## Folder Structure 
'''
.
├── output/                         # Stores outputs from scraping
│   ├── archives/                  # Recycling bin for previous runs
│   ├── pdf_links/                 # JSON files with PDF links (e.g. McKinsey reports)
│   ├── raw_results/               # Raw extracted content from web scraping
│   ├── train_data/                # Training data for classification model
│   └── urls/                      # Tracks visited URLs to avoid revisiting
│
├── scraper/                       # Main scraping scripts
│   ├── dynamic_web_scraper.py     # Script for dynamic pages (load more, pagination)
│   └── website_scraper.py         # Base script orchestrating crawl, extract, clean
│
├── utils/                         # Utility modules used across the tool
│   ├── article_filter.py          # Helpers to filter articles, extract dates, find reports
│   ├── config_loader.py           # Loads scraping URLs and their config settings
│   ├── html_helpers.py            # Extracts and cleans up HTML: removes boilerplate, headers, footers
│   ├── keyword_matcher.py         # Filters articles based on keywords
│   ├── playwright_helpers.py      # Scrolls pages, handles cookie banners (dynamic rendering)
│   ├── sheets_writer.py           # Writes PDFs for McKinsey report relevance checks
│   └── url_tracker.py             # Tracks, saves, loads URLs through crawling sessions
'''


