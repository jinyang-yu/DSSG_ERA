# test_page_scraper.py

import asyncio
import json
import aiohttp
from scraper.page_scraper import PageScraper  # Adjust if needed

async def test():
    scraper = PageScraper("data/test_files/dummy_urls.json", "data/test_files/dummy_visited.json")
    filename = 'data/test_files/globalnews_20250617_test.json'

    results = []

    async with aiohttp.ClientSession() as session:
        for url in scraper.url_dict.keys():
            print(f"\nScraping: {url}")
            text, title, _ = await scraper.fetch_html_async(session, url)
            if text:
                results.append({
                    "url": url,
                    "title": title,
                    "content": text
                })
            else:
                print(f"Failed to extract content from {url}")

    # Save all results to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(results)} articles to {filename}")


if __name__ == "__main__":
    asyncio.run(test())

