# main.py

from scraper.page_scraper import PageScraper
from utils.url_tracker import save_visited
from utils.article_filter import filter_content
from utils.sheets_writer import write_to_tab
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
      results, pdf_list = await scraper.orchestrate_async_crawl(url, keywords)
      total_scraped += len(results)

      if results: 
        timestamp = datetime.now().strftime("%Y%m%d")
        extracted_url = tldextract.extract(url)
        domain = extracted_url.domain or "unknown"
        filename = f"data/raw_results/{domain}_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
           json.dump(results, f, indent=2, ensure_ascii=False)

        filtered_filename = f"data/filtered_results/filtered_{domain}_{timestamp}.json"
        filtered_results = filter_content(results)

        with open(filtered_filename, "w", encoding="utf-8") as f:
           json.dump(filtered_results, f, indent=2, ensure_ascii=False)
           
        print(f"Saved {len(filtered_results)} results to {filtered_filename}")

        for link in pdf_list:
           if not any(item["url"]==link for item in filtered_results):
              pdf_list.remove(link)        

        if len(pdf_list) > 0:
           write_to_tab(timestamp, pdf_list)

        print(f"Saved {len(pdf_list)} links to download PDFs in Google Sheets: dssg_era_pdf_links.")


  print(f"Total pages scraped: {total_scraped}")

  save_visited(scraper.visited_urls, visited_filepath)


if __name__ == "__main__":
    asyncio.run(main())