
from datetime import datetime
import random
import aiohttp
import traceback
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Optional, Dict
from playwright.async_api import async_playwright
from utils.keyword_matcher import KeywordMatcher
from utils.article_filter import extract_published_date, extract_all_published_dates, has_long_title, is_url_blocked, report_filter
from utils.html_helpers import extract_clean_text
from utils.playwright_helpers import handle_cookie_banner, scroll_page_to_bottom

class DynamicWebScraper:
  def __init__(self,  url: str, config: dict, visited_urls: str):
    """
    Initializes DynamicWebScraper

    Args: 
      url_filepath (str): Filepath to JSON of URLs to scrape & corresponding keywords
      visited_filepath (str): Filepath to JSON file containing previously visited URLs
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
      max_retires (int): max number of retries when server issues/network errors, etc.

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
  
  async def paginate_and_collect_links(self, page, base_url: str, max_pages: int) -> dict:
    """
    Navigates through paginated pages, collects and returns all links found.

    Args:
        page: Playwright page object
        base_url (str): Base URL for link extraction
        max_pages (int): Max pagination depth

    Returns:
        dict: All links collected from pagination
    """
    all_links = {}

    for page_num in range(max_pages):
      await page.wait_for_timeout(2000)

      if "enterpriseriskmag.com" in base_url:
            paginated_url = base_url if page_num == 0 else f"{base_url.rstrip('/')}/page/{page_num + 1}/"
            await page.goto(paginated_url)
            await page.wait_for_timeout(2000)
      
      if "thepienews.com" in base_url:
        try:
            older_button = page.locator("a.page-older", has_text="Older")
            if await older_button.count() == 0:
              print("No 'Older' button found. Reached last page.")
              break
            await older_button.first.click()
            print(f"Clicked 'Older' button to go to next page ({page_num + 1})")
            await page.wait_for_timeout(2000)
        except Exception as e:
          print(f"Pagination stopped or failed to click 'Older': {e}")
          break

      if "cbc.ca" in base_url:
        try:
            show_more_button = page.locator("button", has_text="Show More")
            if await show_more_button.count() == 0:
              print("No 'Show More' button found. Reached end.")
              break
            
            previous_count = await page.eval_on_selector_all(
                    "a.cardWrapper-u5T0r", "nodes => nodes.length"
                )
            await page.wait_for_timeout(1000)
            await show_more_button.first.click()
            await page.wait_for_function(
                """(oldCount) => {
                    return document.querySelectorAll('a.cardWrapper-u5T0r').length > oldCount;
                }""",
                arg=previous_count,
                timeout=5000
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
          print(f"Pagination stopped or failed to click 'Show More': {e}")
          break
        
      if "universityaffairs.ca" in base_url:
        try:
            load_more_button = page.locator(".load-more__button", has_text="Load More")
            if await load_more_button.count() == 0:
              print("No 'Load More' button found. Reached end.")
              break
            
            previous_count = await page.eval_on_selector_all(
                    "li.article-block", "nodes => nodes.length"
                )
            await page.wait_for_timeout(1000)
            await load_more_button.first.click()
            await page.wait_for_function(
                """(oldCount) => {
                    return document.querySelectorAll('li.article-block').length > oldCount;
                }""",
                arg=previous_count,
                timeout=5000
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
          print(f"Pagination stopped or failed to click 'Load More': {e}")
          break
        
      if "globalnews.ca" in base_url:
        try:
            load_stories_button = page.locator("button#latestStories-button")
            if await load_stories_button.count() == 0:
              print("No 'Load More Stories' button found. Reached end.")
              break
            
            previous_count = await page.eval_on_selector_all(
                    "li.c-posts__item.c-posts__loadmore", "nodes => nodes.length"
                )
            await page.wait_for_timeout(1000)
            await load_stories_button.first.click()
            await page.wait_for_function(
                """(oldCount) => {
                    return document.querySelectorAll('li.c-posts__item.c-posts__loadmore').length > oldCount;
                }""",
                arg=previous_count,
                timeout=5000
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
          print(f"Pagination stopped or failed to click 'Load More Stories': {e}")
          break
      
      if "mckinsey.com" in base_url:
        try:
            view_more_button = page.locator("button#viewMore")
            if await view_more_button.count() == 0:
              print("No 'View More' button found. Reached end.")
              break
            
            previous_count = await page.eval_on_selector_all(
                    "div.AllInsightsGrid_mck-c-all-insights-grid__grid-item__MhVkU", "nodes => nodes.length"
                )
            await page.wait_for_timeout(1000)
            await view_more_button.first.click()
            await page.wait_for_function(
                """(oldCount) => {
                    return document.querySelectorAll('div.AllInsightsGrid_mck-c-all-insights-grid__grid-item__MhVkU').length > oldCount;
                }""",
                arg=previous_count,
                timeout=5000
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
          print(f"Pagination stopped or failed to click 'View More': {e}")
          break

      if "strategic-risk-global.com" in base_url:
        if page_num == 0:
          paginated_url = base_url
        else: 
          paginated_url = base_url if page_num == 0 else f"{base_url.rstrip('/')}&page={page_num + 1}"
        await page.goto(paginated_url)
        await page.wait_for_timeout(2000)
        
      # if "chronicle.com" in base_url:
      #   try:
      #     items_selector = "div.ListLoadMore-items-item[data-item]"
      #     load_more_button = page.locator("div.ListLoadMore-nextPage a.button-primary", has_text = "Load More")
      #     if await load_more_button.count() == 0:
      #       print("No 'Load More' button found. Reached end.")
      #       break
          
      #     prev_count = await page.eval_on_selector_all(items_selector, "nodes => nodes.length")       
      #     print(f"Clicking 'Load More' button (page {page_num+1})")       
      #     await load_more_button.first.click()
          
      #     for _ in range(10):
      #       current_count = await page.eval_on_selector_all(items_selector, "nodes => nodes.length")
      #       if current_count > prev_count:
      #           print(f"New items loaded: {current_count} > {prev_count}")
      #           break
      #       else:
      #         print("Timeout: no new items loaded after clicking 'Load More'.")
      #         break
      #     await page.evaluate("window.scrollBy(0, 500)")
            
      #       # await page.wait_for_timeout(1000)
          
      #     # await page.wait_for_function(
      #     #   f"""(oldCount) => {{
      #     #       return document.querySelectorAll("{items_selector}").length > oldCount;
      #     #   }}""",
      #     #   arg=prev_count,
      #     #   timeout=8000
      #     # )

      #     await page.wait_for_timeout(2000)
      #   except Exception as e:
      #     print(f"Pagination stopped or failed to click 'Load More': {e}")
      #     break
      
      html = await page.content()
      soup = BeautifulSoup(html, "html.parser")
      dates = extract_all_published_dates(soup)

      new_links = self.extract_links(base_url, soup)
      before_update = len(all_links)
      all_links.update(new_links)

      if any(d.year != 2025 for d in dates):
          print("Found non-2025 content. Stopping pagination.")
          break

      if len(all_links) == before_update:
          print("No new links found. Assuming end of pagination.")
          break
        
      await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
      await page.wait_for_timeout(1000)

    return all_links
      
  async def playwright_and_crawl(self, main_url: str, keywords: List[str], max_pages: int) -> Tuple[str, str, Optional[BeautifulSoup]]:
    """
    Uses Playwright to load and scroll a JavaScript-heavy webpage & crawl
    
    Args:
      main_url (str): The main URL to crawl using Playwright
      keywords (List[str]): List of keyword strings to filter relevant article links
      max_pages (int): Maximum number of pagination pages to crawl when collecting links
    
    Returns:
      Tuple[str, str, Optional[BeautifulSoup]]: 
          - A list of dictionaries containing article content (title, url, text, publish date).
          - A list of URLs to PDFs (if applicable: Mckinsey).
          - None if the process fails due to an exception.
    """
    
    results = []
    pdf_list = []
    visited = set()

    try:
      async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-http2"])
        context = await browser.new_context(
          user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
          locale="en-US",
          java_script_enabled=True,
          viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()

        try:
          await page.goto(main_url, timeout=60000, wait_until="domcontentloaded")
        except Exception as e:
          print(f"[Retrying once] Playwright goto failed: {e}")
          await asyncio.sleep(3)
          await page.goto(main_url, timeout=60000, wait_until="domcontentloaded")

        await handle_cookie_banner(page)
        
        await page.evaluate(
          """async () => {await new Promise(resolve => {let totalHeight = 0;
          const distance = 300;const timer = setInterval(() => {
            window.scrollBy(0, distance); totalHeight += distance;
            if(totalHeight >= document.body.scrollHeight){
              clearInterval(timer);
              resolve();
              }
              }, 200);
              });
              }""")
        
        all_links = await self.paginate_and_collect_links(page, main_url, max_pages=max_pages)
        
        filtered_links = self.matcher.batch_match(all_links, keywords)

        prefiltered_links = {
          url: title
          for url, title in filtered_links.items()
          if (has_long_title(title))
            and url not in visited
            and url not in self.visited_urls
            and not is_url_blocked(url)
         }
        
        for link in all_links:
          print(link)
          visited.add(link)
          if link.rstrip("/") != main_url.rstrip("/"):
            self.visited_urls.add(link)

        for link, title in prefiltered_links.items():
          
          article_title, text, soup = await self.fetch_playwright(page, link)
          if (not soup or has_long_title(title) or link.rstrip("/") == main_url.rstrip("/")):
            continue
          
          published = None
          try:
            published = extract_published_date(soup)
          except Exception:
            pass

            # Only include articles from 2025, or those without a date + not report in Mckinsey (PDF)
          if published and published.year != 2025:
            continue
          
          if link.startswith("https://www.mckinsey.com") and report_filter(soup):
            pdf_list.append(link)

          if text:
            results.append({
              "url": link,
              "title": article_title,
              "content": text,
              "published": published.isoformat() if published else None
              })
            
      await browser.close()
          
      return results, pdf_list
        
    except Exception as e:
      print(f"Playwright Error for {main_url}: {e}")
      traceback.print_exc()
      return "", "", None

  async def fetch_playwright(self, page, url: str) -> Tuple[str, str, Optional[BeautifulSoup]]:
    """
    Uses an existing Playwright page to navigate to a specific URL and load HTML content
    
    Args:
      page: An instance of an active Playwright `Page` object
      url (str): The URL of the article/page to fetch and scrape
    
    Returns: 
      Tuple[str, str, Optional[BeautifulSoup]]: 
          - Title of the article/page
          - Cleaned main text content
          - Parsed BeautifulSoup object of the full HTML
    """
    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")

        await handle_cookie_banner(page)
        if "chronicle" in url:
          content = await page.content()
          if ("Verifying you are human" in content or "Just a moment..." in content):
            print(f"Cloudflare challenge detected on {url}. Waiting for manual solve...")
            await page.wait_for_selector('div.ListLoadMore-items-item', timeout=0)
            print("Challenge solved, continuing...")
            await scroll_page_to_bottom(page)
            
            await page.wait_for_selector('div.ArticlePage-articleBody.contentBOdy.fdIn', timeout=30000)
            
        await scroll_page_to_bottom(page)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        title, text = extract_clean_text(html, url, self.config)

        return title, text, soup

    except Exception as e:
        print(f"Playwright Error during fetch of {url}: {e}")
        traceback.print_exc()
        return "", "", None

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

  async def orchestrate_async_crawl(self, main_url: str, keywords: List[str]) -> List[Dict]:
    """
    Starts the async crawl from the main page of URL using keyword filtering & depth

    Args:
      main_url (str): Main page URL to scrape
      keywords (List[str]): List of keywords to restrict search

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
        if (not soup or has_long_title(title) or link.rstrip("/") == main_url.rstrip("/")):
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
          
      else:
        results, pdf_list = await self.playwright_and_crawl(main_url, keywords, max_pages=10)
          
      return results, pdf_list
    