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
   - This method embeds the title and keywords (SentenceTransformers) then does the following:
       - Includes the article if the max cosine similarity between the title and any of the keywords >= threshold
       - If the max cosine similarity score is within a close range near the threshold, it'll do an additional check:
           - Predicts CrossEncoder scores between each pair of title and keyword, and includes the article if it's greater than the threshold
   - Currently, the threshold is set on the lower end (0.3) to capture more content, but this can be changed in `utils/keyword_matcher.py`  
5. Additional filter on the following checks
    - URL has not been visited before from all completed runs
    - URL has not been visited before in this current session
    - Title is > 2 words (most likely not other info pages)
    - Follows specified path for that given URL (either path patterns that articles live on, or paths to avoid for irrelevant sections)
6. For all article links, fetch title, content, HTML through BeautifulSoup
7. Clean article content (remove boilerplate, headers, etc.) through Python libraries: newspaper or boilerpy3
8. Filter for 2025 content
9. Handle Mckinsey reports in PDF list
10. Save all articles into each respective JSON file: *domain_date.json*

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

**Changing number of pages scraped**:
If you'd like to change the number of pages/buttons the scraper goes through, change the argument `max_pages` on line 592 in the method `orchestrate_async_crawl` in file `scraper/dynamic_web_scraper.py`
```Python
results, pdf_list = await self.playwright_and_crawl(main_url, keywords, max_pages=10)
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

## How to Add More URLs? 
  1)  Configure the initial URL settings in `data/inputs/websites/urls.json`
       - Format:
         ```Python
         {"new_url.com": {
             "keywords":[],
             "allowed_paths": []
             "method": "boilerplate"
             "use_playwright": 0
           }
         }
         ```
  2)  Inspect the source and check for any patterns in the path that articles live on, or any to avoid
       - If you find a pattern that articles live on, you will add them into ```'allowed_paths':[...]``` in the URL config in step 1)
       - If you don't find any patterns that articles live on, you can add any blocked paths into ```'blocked_paths':[...]``` in the URL config in step 1)
  3) If there are any keywords that are relevant to refine the search, add them into ```keywords: [...]``` in the URL config in step 1)
  4) If you'd like to trial run to see how the content extraction looks on default settings, delete other URLs in `../data/inputs/websites/urls.json` to see how this       one website performs (without having to run all the other ones)
  5) In the case that the content extraction looks clean, while manually comparing to what lives on the website:
     - No other URL configuration needs to be added
  6) In the case that the URL content extraction is very messy, empty or not representative, check the following:
     - Inspect if the results change, as it may be a dynamically rendered site, by changing the config `"use_playwright": 1` and `"method": "default"`
     - Inspect the HTML structure. Make sure to check the following:
         - The main website page, and the tags/elements that link to the articles, and their titles
             - This will help extract the links from the main source properly
             - You can add any specific selections in `scraper/website_scraper.py` in the `extract_links` method
         - The respective article pages, and the tags/elements that indicate the title and website body
             - This will help extract article content properly
     - If you find that there is a pattern in the elements that wrap article content for this specific URL, you can add them into the URL config file in the key,         like the following example:
       ```Python
       "selectors": {"title: ["h1", {"class": "l-article__title"}],
                     "article": ["article", {"class": "l-article__text js-story-text"}]}
       ```
     - If even after inspection, the source seems complex, handle the URL separately, through a custom extraction function. Mckinsey.com is an example, if general       guidance is needed on the structure. It'll be altered in the URL config files, and `utils/html_helpers.py`
  7) If the content looks generally good, but you find certain boilerplate patterns, you can remove them through REGEX in `../classifier/utils/domain_patterns.py`
  8) When version 2 is being used, do the following first 7 steps, in addition to inspecting the button/pages HTML structure and add them in `scraper/dynamic_web_scraper.py` in the `paginate_and_collect_links` method
     






