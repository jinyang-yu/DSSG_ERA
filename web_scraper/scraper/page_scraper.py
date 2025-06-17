# scraper/article_scraper.py 

import random
import aiohttp
import traceback
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Optional, Dict

from utils.url_tracker import load_visited, load_urls
from utils.keyword_matcher import KeywordMatcher
from utils.site_rules import SITE_RULES
from utils.article_filter import extract_published_date, is_article_url, has_long_title, check_valid_article

class PageScraper:
  def __init__(self, url_filepath: str, visited_filepath: str):
    """
    Initializes PageScraper

    Args: 
      url_filepath (str): Filepath to JSON of URLs to scrape & corresponding keywords
      visited_filepath (str): Filepath to JSON file containing previously visited URLs
    """
    self.url_filepath = url_filepath
    self.visited_filepath = visited_filepath

    self.visited_urls = load_visited(self.visited_filepath)
    self.url_dict = load_urls(self.url_filepath)
    self.matcher = KeywordMatcher()

    self.semaphore = asyncio.Semaphore(3)



  async def fetch_html_async(self, session: aiohttp.ClientSession, url: str, max_retries: int = 3) -> Tuple[str, str, Optional[BeautifulSoup]]:
    """
    Fetch HTML content from the URL asynchronously with retry and backoff

    Args:
      session (aiohttp.ClientSession): shared session for all requests
      url (str): main url to scrape
      max_retires (int): max number of retries when server issues/network errors, etc.

    Returns: 
      Tuple containing: 
      - text (str): visible text from the page
      - title (str): title of the page, empty str if none
      - soup (BeautifulSoup or none): Parsed HTML or None if error
    """

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

    # Acquire the semaphore here to limit concurrency
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
                      # fallback decoding if utf-8 or declared charset fails
                        html = raw.decode('latin-1', errors='replace')

                      soup = BeautifulSoup(html, "html.parser")
                      text_html, title = self.extract_clean_text(html)

                      await asyncio.sleep(random.uniform(1, 3))

                      return text_html, title, soup

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
  
  def extract_clean_text(self, html:str) -> Tuple[str, str]:
    """
    Extracts clean and readable text and title from HTML content

    Args:
      html (str): Raw HTML content pulled

    Returns: 
      Tuple[str, str]: Cleaned text content and page title
    """

    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    # remove script, style and hidden elements
    for tag in soup(["script", "style", "noscript", "video", "iframe", "embed", "object"]):
      tag.decompose()

    for hidden in soup.select('[style*="display:none"], [style*="visibility:hidden"]'):
      hidden.decompose()

    # # add new line before block-level elements
    # for tag in soup.find_all(["p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article"]):
    #     tag.insert_before("\n")

    # text = soup.get_text()
    # lines = [line.strip() for line in text.split("\n") if line.strip()]
    # cleaned_text = "\n".join(lines)
    cleaned_html = str(soup.body) if soup.body else str(soup)

    return cleaned_html, title


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
    if soup is None: 
      return links

    base_domain = urlparse(base_url).netloc
    for a_tag in soup.find_all("a", href=True):
      href = a_tag["href"]
      # convert relative URLs to absolute
      abs_url = urljoin(base_url, href)
      parsed_url = urlparse(abs_url)
      # restricts urls to http/https & domains from external sites
      if parsed_url.scheme not in ["http", "https"]: 
        continue
      if parsed_url.netloc != base_domain:
        continue
      # removes fragment identifier and / at end of URLs
      clean_url = abs_url.split("#")[0].rstrip("/")

      # skip blocked URLs
      if self.is_url_blocked(clean_url):
        continue
      link_title = a_tag.get_text(strip=True) or ""
      links[clean_url] = link_title

    return links
  
  def is_url_blocked(self, url: str) -> bool: 
    """
    Checks if the URL is blocked in utils/site_rules.py to avoid unnecessary scraping 

    Args:
      url (str): URL to check if adheres to configured site_rules.py 

    Returns:
      bool: True if URL blocked according to site_rules.py
    """

    parsed = urlparse(url)
    domain = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.lower() or "/"

    domain_rules = SITE_RULES.get(domain, {})

    # blocked paths
    blocked_paths = domain_rules.get("blocked_paths", [])
    allowed_paths = domain_rules.get("allowed_paths", [])
    # if len(blocked_paths) > 0:
    #    return any(path.startswith(p) for p in blocked_paths)

    # # allowed paths
    # elif len(allowed_paths) > 0:
    #   return not any(substr in path for substr in allowed_paths)
    
    # else:
    #    return False

    if blocked_paths:
        if any(path.startswith(p) for p in blocked_paths):
            return True

    if allowed_paths:
        if not any(substr in path for substr in allowed_paths):
            return True

    else:
      return False

  
  
  async def orchestrate_async_crawl(self, main_url: str, keywords: List[str]) -> List[Dict]:
    """
    Starts the async crawl from the main page of URL using keyword filtering & depth

    Args:
      main_url (str): Main page URL to scrape
      keywords (List[str]): List of keywords to restrict search

    Returns: 
      List[Dict]: Scraped content from website
    """

    async with aiohttp.ClientSession() as session: 
      results = []
      visited = set()

      # 1) fetch and parse main page data 
      text, title, soup = await self.fetch_html_async(session, main_url)
      if not soup:
         return results
      
      # 2) extract article links directly from main page
      links = self.extract_links(main_url, soup)
      filtered_links = self.matcher.batch_match(links, keywords)

      # prefiltered_links = {
      #    url: title for url, title in filtered_links.items()
      #    if is_article_url(url) or has_long_title(title)
      # }

      prefiltered_links = {
        url: title
        for url, title in filtered_links.items()
        if (is_article_url(url) or has_long_title(title))
          and url not in visited
          and url not in self.visited_urls
          and not self.is_url_blocked(url)
    }
      
      for link in links:
        visited.add(link)
        if link.rstrip("/") != main_url.rstrip("/"):
          self.visited_urls.add(link)

      for link, title in prefiltered_links.items():

        text, title, soup = await self.fetch_html_async(session, link)
        if (not soup or 
            not check_valid_article(link, soup, title) or 
            link.rstrip("/") == main_url.rstrip("/")):
            continue
        
        published = None
        try:
          published = extract_published_date(soup)
        except Exception:
           pass

          # Only include articles from 2025, or those without a date
        if published and published.year != 2025:
           continue
         
        if text:
           results.append({
              "url": link,
              "title": title,
              "content": text,
              "published": published.isoformat() if published else None
            })

      return results