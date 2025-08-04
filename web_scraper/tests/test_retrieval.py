import json
from newspaper import Article
from playwright.async_api import TimeoutError, Error
from scraper.page_scraper import PageScraper
from utils.article_filter import extract_published_date
import asyncio
from bs4 import BeautifulSoup
import aiohttp
from boilerpy3 import extractors

STATIC_SITES = ["universityworldnews.com", "esgtoday.com"]

def clean_extracted_text(raw_text: str, html: str, url: str) -> str:
    """Use Newspaper to post-clean extracted article text."""
    article = Article(url='')
    article.set_html(html)
    try:
        article.parse()
        return article.text.strip() if article.text else raw_text
    except Exception:
        return raw_text  # fallback if Newspaper fails
    
def clean_boilerplate(raw_text, html, url):
    extractor = extractors.ArticleExtractor()
    try:
        content = extractor.get_content(html)
        return content.strip() if content else raw_text
    except Exception:
        return raw_text

async def fetch_html(url: str) -> tuple[str, str, BeautifulSoup]:
    """Fetch raw HTML/text without Playwright."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    raw_text = soup.get_text(separator="\n", strip=True)
    return title, raw_text, soup


async def clean_playwright(input_file: str, output_file: str):
    scraper = PageScraper(url_filepath="", visited_filepath="")  # no persistence

    with open(input_file, "r") as f:
        data = json.load(f)

    urls = [item["url"] for item in data]
    cleaned_results = []
    count = 0

    async with scraper._get_playwright_context() as browser_page:
        browser = browser_page.context.browser  # single browser

        for url in urls:
            retries = 2
            while retries > 0:
                try:
                    print(f"Fetching: {url}")

                    # Use plain HTML fetch for static sites
                    if any(domain in url for domain in STATIC_SITES):
                        title, raw_text, soup = await fetch_html(url)
                    else:
                        page = await browser.new_page()
                        title, raw_text, soup = await scraper.fetch_playwright(page, url)
                        await page.close()

                    if not raw_text:
                        print(f"Skipping {url}: no content")
                        break

                    # Post-clean with Newspaper
                    cleaned_text = clean_boilerplate(raw_text, str(soup), url)

                    # Extract published date
                    try:
                        published = extract_published_date(soup)
                        published = published.isoformat() if published else None
                    except Exception:
                        published = None

                    cleaned_results.append({
                        "url": url,
                        "title": title,
                        "content": cleaned_text,
                        "published": published
                    })

                    count += 1
                    print(f"Scraped {count}/{len(urls)} URLs successfully")
                    break

                except (TimeoutError, Error) as e:
                    retries -= 1
                    print(f"Playwright error for {url}: {e}. Retries left: {retries}")
                    if retries == 0:
                        print(f"Skipping {url} after multiple failures")

    with open(output_file, "w") as f:
        json.dump(cleaned_results, f, indent=2)

    print(f"Saved cleaned results to {output_file}")

if __name__ == "__main__":
    INPUT_FILE = "data/train_data/esgtoday_20250719_train.json"
    OUTPUT_FILE = "data/raw_results/esgtoday_20250719_rerun.json"
    asyncio.run(clean_playwright(INPUT_FILE, OUTPUT_FILE))
