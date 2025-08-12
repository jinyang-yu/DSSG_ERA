# Web-Scraping Tool 
This folder contains the files to run the web-scraping tool, of 11 different URLs and saves the extracted content. 

## Folder Structure 
```
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
├── credentials.json               # Credentials file downloaded for credentials from Google Service Account   
```

## URL Configurations
The website branch data is initialized through the main data folder, in websites/urls.json 

The urls.json file consists of information for each source, all found through experimentation + trial and error, such as: 
- Keywords: keywords provided to refine the search
- Allowed paths: path patterns that represent article/story URLs 
- Blocked paths: path patterns that represent irrelevant pages
- Method: method for content retrieval
  - custom: specific to source -> Mckinsey
  - default: HTML playwright -> BeautifulSoup content extraction -> clean through newspaper library
  - newspaper: fetch all content through newspaper library
  - boilerplate: BeautifulSoup HTML and content extraction -> clean through boilerpy3 library
- Selectors: specific CSS selectors to locate title/content elements based on site's HTML structure
- Use playwright: 0 if static HTML or 1

## Scraping Versions
This project includes **two versions** of a web-scraping tool, where either or can be utilized for the specific use-case

### **Version 1 - Basic Tool**
**Purpose**: Extracting articles on a more frequent basis

**Basic Workflow**: 
1. Extract main page HTML
   - Static HTML websites (esgtoday.com, universityworldnews.com) fetched through BeautifulSoup
   - Dynamically rendered websites (all others) fetched initially through Playwright
2. Extract article links from main page
3. Pre-filter based on article title & keywords, if present
4. Additional filter on the following checks
    - URL has not been visited before from all completed runs
    - URL has not been visited before in this current session
    - Title is > 2 words (most likely not other info pages)
    - Follows specified path for that given URL (either path patterns that articles live on, or paths to avoid for irrelevant sections)
5. For all article links, fetch title, content, HTML through BeautifulSoup
6. Clean article content (remove boilerplate, headers, etc.) through Python libraries: newspaper or boilerpy3
7. Filter for 2025 content
8. Handle Mckinsey reports in PDF list
9. Save all articles into each respective JSON file: *domain_date.json*

### **Version 2 - Dynamic Loading Tool**
**Purpose**: Extracting articles for an extended time period

**Enhancement**: Implements specific cases for buttons on each source (e.g., load more, pagination, view more, etc.)

**Added Implementations**: 
- All steps from the basic workflow are relatively the same, but ones with pagination/loading are handled separately to ones that don't
- Dynamically interacts with loading buttons and page numbers
- Includes scrolling
- Fetches HTML through Playwright then BeautifulSoup for content extraction

**How to Run Version 2**:
In `run_scraper.py`, comment out WebsiteScraper, and uncomment out DynamicWebScraper: 
```Python
# scraper = WebsiteScraper(url= url, config=settings, visited_urls=visited_urls)
# for loading dynamic web-scraper
scraper = DynamicWebScraper(url= url, config=settings, visited_urls=visited_urls)
```

## Key Considerations 
- **Chronicle.com**:
    - Had issues with Cloudflare human verification flag
    - This web-scraping tool is not currently configured for chronicle.com in the dynamic web-scraping version
- **Mckinsey.com**:
    - The Mckinsey site consists of PDF reports that needs manual downloading that was not implemented in this version of the pipeline. Therefore, each run, it will check if any new reports have surfaced on the site and save these links separately into a Google Sheets file, which can be accessed [here](https://docs.google.com/spreadsheets/d/1L7xnQGCdX7L8Hczp1uqtrr8FMfyk5Yyf3ud2LZ2MfsA/edit?usp=sharing)
    - The Google Sheets API call was completed through a service account and the corresponding credentials, that should be saved under `credentials.json` in the root `web_scraper/` folder
- **URLs Prone to Timeout & Fetch Failures**
    - chronicle.com
    - cbc.ca
    - mckinsey.com






