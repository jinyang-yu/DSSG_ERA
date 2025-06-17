# main.py

from scraper.page_scraper import PageScraper
from utils.url_tracker import save_visited
from utils.content_cleaner import content_cleaner
from datetime import datetime
import json
import asyncio
import tldextract


async def main():
  # load urls and keywords from data/urls.json
  url_filepath = "data/urls/urls.json"
  visited_filepath = "data/urls/visited_urls.json"

  scraper = PageScraper(url_filepath, visited_filepath)

  total_scraped = 0

  for url, keywords in scraper.url_dict.items():
      print(f"Processing: {url}")
      results = await scraper.orchestrate_async_crawl(url, keywords)
      total_scraped += len(results)

      if results: 
        timestamp = datetime.now().strftime("%Y%m%d")
        extracted_url = tldextract.extract(url)
        domain = extracted_url.domain or "unknown"
        filename = f"data/raw_results/{domain}_{timestamp}.json"
        # clean_filename = f"data/clean_results/{domain}_{timestamp}_clean.json"
        
        with open(filename, "w", encoding="utf-8") as f:
           json.dump(results, f, indent=2, ensure_ascii=False)

        # clean_results = content_cleaner(results)

        # with open(clean_filename, "w", encoding="utf-8") as f:
        #    json.dump(clean_results, f, indent=2, ensure_ascii=False)
           
        print(f"Saved {len(results)} results to {filename}")


  print(f"Total pages scraped: {total_scraped}")

  save_visited(scraper.visited_urls, visited_filepath)


if __name__ == "__main__":
    asyncio.run(main())