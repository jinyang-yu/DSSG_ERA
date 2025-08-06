
from datetime import datetime
import random
import aiohttp
import traceback
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Optional, Dict
from playwright.async_api import async_playwright
from web_scraper.utils.keyword_matcher import KeywordMatcher
from web_scraper.utils.article_filter import extract_published_date, has_long_title, is_url_blocked, report_filter
from web_scraper.utils.html_helpers import extract_clean_text
from web_scraper.utils.playwright_helpers import handle_cookie_banner, scroll_page_to_bottom

class WebsiteScraper:
  """
    Asynchronous web scraper that fetches HTML content, extracts titles and bodies,
    handles dynamic pages with Playwright, filters links, and performs keyword-based crawling.
  """
  def __init__(self, url: str, config: dict, visited_urls: str):
    """
    Initializes WebsiteScraper

    Args: 
      url (str): url to scrape 
      config (dict): dictionary of settings for each url
    """
    self.start_url = url
    self.config = config
    self.use_playwright = config.get("use_playwright", 0)
    self.domain = config.get("domain", "")
    self.keywords = config.get("keywords", [])
    self.visited_urls = visited_urls
    
    self.matcher = KeywordMatcher()

    self.semaphore = asyncio.Semaphore(3)

  async def fetch_html_async(self, session: aiohttp.ClientSession, url: str, max_retries: int = 3) -> Tuple[str, str, Optional[BeautifulSoup]]:
    """
    Fetch HTML content from the URL asynchronously with retry and backoff

    Args:
      session (aiohttp.ClientSession): shared session for all requests
      url (str): main url to scrape
      max_retries (int): max number of retries when server issues/network errors, etc.

    Returns: 
      Tuple containing: 
      - text (str): visible text from the page
      - title (str): title of the page, empty str if none
      - soup (BeautifulSoup or none): Parsed HTML or None if error
    """
    print(f"Fetching URL: {url}")
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
    "DNT": "1",  # Do Not Track
    "Connection": "keep-alive"}

    retry_count = 0
    backoff_delay = 1
    timeout = aiohttp.ClientTimeout(total=50)

    async with self.semaphore:
      while retry_count <= max_retries:
        try:
          async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
              raw = await response.read()
              encoding = response.charset or 'utf-8'
              try:
                html = raw.decode(encoding)
              except UnicodeDecodeError:
                html = raw.decode('latin-1', errors='replace')

              soup = BeautifulSoup(html, "html.parser")
              title, text = extract_clean_text(html, url, self.config)

              await asyncio.sleep(random.uniform(1, 3))

              return title, text, soup

            elif response.status == 429:
              retry_after = int(response.headers.get("Retry-After", 10))
              print(f"429 Too Many Requests. Sleeping for {retry_after}s before retrying {url}")
              await asyncio.sleep(retry_after)
              retry_count += 1
              continue

            else:
              print(f"Error {response.status} fetching {url}")
              return "", "", None

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
          print(f"Error scraping {url}: {repr(e)} (attempt {retry_count + 1}/{max_retries})")
          traceback.print_exc()
          if retry_count == max_retries:
            break

          await asyncio.sleep(backoff_delay)
          backoff_delay *= 2
          retry_count += 1

    return "", "", None

  async def fetch_html_with_playwright(self, url: str) -> Tuple[str, str, Optional[BeautifulSoup]]:
    """
    Fetches content using Playwright for dynamic pages.
    
    Args:
      url (str): The target URL to fetch.

    Returns:
      Tuple[str, str, Optional[BeautifulSoup]]:
        - title (str): Extracted title of the page, or empty string if not found.
        - text (str): Extracted main text content of the page, or empty string.
        - soup (BeautifulSoup or None): Parsed HTML soup object or None on failure.

    Raises:
      None: Errors are caught internally; failure returns empty content and None.
    """
    
    # print(f"Fetching URL with Playwright: {url}")
    async with async_playwright() as p:
      browser = await p.chromium.launch(headless=True, args=["--disable-http2"])
      context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="en-US",
        java_script_enabled=True,
        viewport={"width": 1366, "height": 768},
      )
      page = await context.new_page()

      try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await handle_cookie_banner(page)
        await scroll_page_to_bottom(page)
        await page.wait_for_timeout(3000)  # Wait for JavaScript to render
        

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        # print(f"Fetched HTML for {url[:80]}... (length={len(html)})")

        title, text = extract_clean_text(html, url, self.config)
        # print(f"Extracted title: {title}")
        # print(f"Extracted content (first 300 chars): {text[:300]}")

        return title, text, soup

      except Exception as e:
        print(f"Error fetching content with Playwright: {e}")
        return "", "", None
      finally:
        await page.close()
        await browser.close()

  def extract_links(self, base_url: str, soup: BeautifulSoup) -> dict:
    """
    Extracts valid URLs from main (domain) page

    Args:
      base_url (str): URL of page being parsed
      soup (BeautifulSoup): Parsed HTML content of the page

    Returns:
      dict: Dictionary of absolute, clean URLs from main page: title of page
    """

    links = {}
    if not soup:
      return links

    for a_tag in soup.find_all("a", href=True):
      href = a_tag["href"]
      abs_url = urljoin(base_url, href)
      parsed_url = urlparse(abs_url)

      if parsed_url.scheme not in {"http", "https"}:
        continue
      
      if not (parsed_url.netloc == self.domain or parsed_url.netloc.endswith("." + self.domain)):
        continue

      clean_url = abs_url.split("#")[0].rstrip("/")

      if is_url_blocked(clean_url, self.config):
        continue

      # Special case for enterpriseriskmag.com filtering by year 2025
      if "enterpriseriskmag.com" in self.domain:
        parent = a_tag.parent
        if parent:
          date_span = parent.find_next("span", class_="u-meta-date u-meta-icon")
          if date_span:
            date_text = date_span.get_text(strip=True)
            try:
              published_date = datetime.strptime(date_text, "%d %B %Y")
              if published_date.year != 2025:
                continue  
            except ValueError:
              pass

      link_title = (
        a_tag.get("title")
        or a_tag.get("aria-label")
        or a_tag.get_text(strip=True)
        or ""
      )

      links[clean_url] = link_title

    return links

  
  async def orchestrate_async_crawl(self, main_url: str) -> List[Dict]:
    """
    Starts the async crawl from the main page of URL using keyword filtering & depth

    Args:
      main_url (str): Main page URL to scrape

    Returns: 
      List[Dict]: Scraped content from website
    """
    # print(f"Starting crawl for {main_url}")
    async with aiohttp.ClientSession() as session: 
      results = []
      pdf_list = []
      visited = set()

      # 1) fetch and parse main page data 
      if self.use_playwright == 0: 
        title, text, soup = await self.fetch_html_async(session, main_url)
      else:
        title, text, soup = await self.fetch_html_with_playwright(main_url)
      
      if not soup or not text.strip():
        print(f"Skipping URL due to fetch failure or empty content: {main_url}")
        return results, pdf_list
        
      links = self.extract_links(main_url, soup)
      filtered_links = self.matcher.batch_match(links, self.keywords)
      
      prefiltered_links = {
        url: title
        for url, title in filtered_links.items()
        if (has_long_title(title))
          and url not in visited
          and url not in self.visited_urls
          and not is_url_blocked(url, self.config)
        }
      
      for link in links:
        visited.add(link)
        if link.rstrip("/") != main_url.rstrip("/"):
          self.visited_urls.add(link)
      
      # print(f"Found {len(prefiltered_links)} links to scrape from main page.")
      # for link in prefiltered_links.keys():
      #   print(f"Scheduling scraping of URL: {link}")
      
      tasks = [
            self.fetch_html_async(session, link)
            for link in prefiltered_links.keys()
        ]
      
      fetched_results = await asyncio.gather(*tasks)
          
      for (title, text, soup), link in zip(fetched_results, prefiltered_links.keys()):
        if not soup or not text.strip():
          print(f"Skipping URL due to fetch failure or empty content: {link}")
          continue
        if (not soup or not has_long_title(title) or link.rstrip("/") == main_url.rstrip("/")):
          continue
        
        published = None
        try:
          published = extract_published_date(soup)
        except Exception:
          pass

        if published and published.year != 2025:
          continue
        
        if self.domain == "mckinsey.com" and report_filter(soup):
          pdf_list.append(link)
        
        if text:
          results.append({
            "url": link,
            "title": title,
            "content": text,
            "published": published.isoformat() if published else None
            })
          
    return results, pdf_list
    