# Web-Scraping Tool 
This folder contains the files to run the web-scraping tool, of 11 different URLs and saves the extracted content. 

## Folder Structure 
```
.
├── output/                        # Stores outputs from scraping
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
│
├── run_scraper.py                 # Main file to run encapsulating web-scraping workflow
```

## URL Configurations

## Scraping Versions
This project includes **two versions** of a web-scraping tool, where either or can be utilized for the specific use-case

### **Version 1 - Basic Tool**
- **Purpose**: Extracting articles on a more frequent basis
- **Workflow**:
  1. Extract main page HTML
     a) Static HTML websites (esgtoday.com, universityworldnews.com) fetched through BeautifulSoup
     b) Dynamically rendered websites (all others) fetched initially through Playwright
  2. Extract article links from main page
  3. Pre-filter based on article title & keywords, if present
  4. Additional filter on the following checks:
     a) URL has not been visited before from all completed runs
     b) URL has not been visited before in this current session
     c) Title is > 2 words (most likely not other info pages)
     d) Follows specified path for that given URL (either path patterns that articles live on, or paths to avoid for irrelevant sections)
  5. For all article links, fetch HTML content through BeautifulSoup
  6. Filter for 2025 content
  7. Handle Mckinsey reports in PDF list
  8. Save all articles into each respective JSON file: *domain_date.json*

### **Version 2 - Dynamic Loading Tool**
- **Purpose**: Extracting articles for an extended time period
- **Differentiation**: Implements specific cases for buttons on each source (e.g., load more, pagination, view more, etc.)



