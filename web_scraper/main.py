# main.py

from scraper.website_scraper import WebsiteScraper
from utils.url_tracker import save_visited, load_visited
from utils.config_loader import load_url_config
from utils.sheets_writer import write_to_tab
from datetime import datetime
import json
import asyncio
import tldextract


async def main():
    visited_filepath = "data/urls/visited_urls.json"
    url_filepath = "data/urls/urls.json"
    config = load_url_config(url_filepath)
    visited_urls = load_visited(visited_filepath)

    total_scraped = 0

    for url, settings in config.items():
        print(f"Processing: {url}")
        scraper = WebsiteScraper(url= url, config=settings, visited_urls=visited_urls)
        # for loading web-scraper
        # scraper = DynamicWebScraper(url= url, config=settings, visited_urls=visited_urls)
        results, pdf_list = await scraper.orchestrate_async_crawl(url)
        total_scraped += len(results)
        visited_urls.update(scraper.visited_urls)

        if results:
            timestamp = datetime.now().strftime("%Y%m%d")
            extracted_url = tldextract.extract(url)
            domain = extracted_url.domain or "unknown"
            filename = f"data/raw_results/{domain}_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            updated_pdf_list = []
            for link in pdf_list:
                for item in results:
                    if item["url"] == link:
                        results.remove(item)
                        updated_pdf_list.append(link)
                        break  

            print(f"Saved {len(results)} results to {filename}")

            pdf_list[:] = updated_pdf_list  

        if len(pdf_list) > 0:
            write_to_tab(timestamp, pdf_list)

            print(
                f"Saved {len(pdf_list)} links to download PDFs in Google Sheets: dssg_era_pdf_links."
            )

    print(f"Total pages scraped: {total_scraped}")

    save_visited(scraper.visited_urls, visited_filepath)


if __name__ == "__main__":
    asyncio.run(main())
