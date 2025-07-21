
import random
import aiohttp
import traceback
import asyncio
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Optional, Dict
from playwright.async_api import async_playwright
import re

from utils.url_tracker import load_visited, load_urls
from utils.keyword_matcher import KeywordMatcher
from utils.site_rules import SITE_RULES
from utils.article_filter import extract_published_date, extract_all_published_dates, is_article_url, has_long_title, check_valid_article, has_article_structure
from utils.pdf_filter import report_filter

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
            "Connection": "keep-alive"
        }

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
                            title, text = self.extract_clean_text(html)

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

    def extract_clean_text(self, html: str) -> Tuple[str, str]:
        """
        Extracts a cleaned-up title and article content from raw HTML.

        Args:
            html (str): The raw HTML string.

        Returns:
            Tuple[str, str]: (title, cleaned_content)
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove non-content tags
        for tag in soup(["script", "style", "noscript", "video", "iframe", "embed", "object"]):
            tag.decompose()

        # Remove hidden content
        for hidden in soup.select('[style*="display:none"], [style*="visibility:hidden"]'):
            hidden.decompose()

        # Remove irrelevant sections like ads, related articles, footers
        for tag in soup.find_all(['div', 'section', 'aside']):
            if tag is None or not hasattr(tag, 'get'):
                continue
            if getattr(tag, 'name', None) is None:
                continue
            try:
                tag_classes = tag.get('class')
            except Exception:
                continue

            class_str = " ".join(tag_classes) if isinstance(tag_classes, list) else str(tag_classes or "")
            tag_id = tag.get('id') or ""

            if any(keyword in class_str.lower() for keyword in [
                "related", "recommend", "trending", "ad", "advertisement", "sponsored", "more-article", "promo", "footer"
            ]) or any(keyword in tag_id.lower() for keyword in [
                "related", "recommend", "trending", "ad", "promo", "footer"
            ]):
                tag.decompose()

        # Extract the title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        else:
            h1 = soup.find("h1")
            if h1 and h1.get_text(strip=True):
                title = h1.get_text(strip=True)
            else:
                title = soup.title.string.strip() if soup.title and soup.title.string else ""

        allowed_classes = {
            "article__body", "ArticlePage-articleBody", "main-article", "content-body",
            "td-post-content", "entry-content", "post-content", "single-article", "post-body",
            "tdb-single-content", "tdb-block-inner", "tdb-content", "single-content"
        }

        # Try to find article container with allowed classes or fallback
        article_container = (
            soup.find("article") or
            next((tag for tag in soup.find_all("div", class_=lambda c: c and any(allowed in cls for cls in c for allowed in allowed_classes))), None)
        )
        if not article_container:
            divs = soup.find_all('div')
            article_container = max(divs, key=lambda d: len(d.find_all('p')), default=None)

        container = article_container if article_container else soup

        # Insert newlines before block elements to preserve structure
        for tag in container.find_all([
            "p", "div", "br", "li", "ul", "ol",
            "h1", "h2", "h3", "h4", "h5", "h6",
            "section", "article"
        ]):
            tag.insert_before("\n")

        # Extract and clean the text
        text = container.get_text()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned_text = "\n".join(lines)

        return title, cleaned_text

    def no_playwright(self, url: str) -> bool:
        """
        Checks if source is universityworldnews.com or esgtoday.com

        Args:
          url (str): URL of source

        Returns:
          bool: True if URL not needing playwright

        """

        return any(domain in url for domain in ["universityworldnews.com", "esgtoday.com"])

    async def paginate_and_collect_links(self, page, base_url: str, max_pages: int = 5) -> dict:
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

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            new_links = self.extract_links(base_url, soup)
            all_links.update(new_links)

            dates = extract_all_published_dates(soup)
            if any(d.year != 2025 for d in dates):
                print("Found non-2025 content. Stopping pagination.")
                break

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

            # Scroll after clicking 'Older' to load lazy content
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)

        return all_links

    async def handle_cookie_banner(self, page):
        try:
            await page.locator("#onetrust-accept-btn-handler").click(timeout=5000)
            await page.wait_for_timeout(1000)
            print("Accepted cookies.")
        except Exception:
            print("No cookie banner found or failed to click.")

    async def fetch_playwright(self, url: str) -> Tuple[List[Dict], List[str]]:
        results = []
        pdf_list = []

        try:
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
                except Exception as e:
                    print(f"[Retrying once] Playwright goto failed: {e}")
                    await asyncio.sleep(3)
                    await page.goto(url, timeout=60000, wait_until="domcontentloaded")

                await self.handle_cookie_banner(page)

                await page.evaluate("""async () => {
                    await new Promise(resolve => {
                        let totalHeight = 0;
                        const distance = 300;
                        const timer = setInterval(() => {
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            if(totalHeight >= document.body.scrollHeight){
                                clearInterval(timer);
                                resolve();
                            }
                        }, 200);
                    });
                }""")
                await page.wait_for_timeout(3000)

                all_links = await self.paginate_and_collect_links(page, url)

                for link, title in self.matcher.batch_match(all_links, []).items():
                    if not is_article_url(link) or link in self.visited_urls or self.is_url_blocked(link):
                        continue

                    article_page = await context.new_page()
                    try:
                        await article_page.goto(link, timeout=60000, wait_until="domcontentloaded")
                        await article_page.evaluate("""async () => {
                            await new Promise(resolve => {
                                let totalHeight = 0;
                                const distance = 300;
                                const timer = setInterval(() => {
                                    window.scrollBy(0, distance);
                                    totalHeight += distance;
                                    if(totalHeight >= document.body.scrollHeight){
                                        clearInterval(timer);
                                        resolve();
                                    }
                                }, 200);
                            });
                        }""")
                        await article_page.wait_for_timeout(3000)

                        html = await article_page.content()
                        print(f"Fetched HTML for {link[:80]}... (length={len(html)})")
                        soup = BeautifulSoup(html, "html.parser")

                        title, text = self.extract_clean_text(html)
                        print(f"Extracted title: {title}")
                        print(f"Extracted content (first 300 chars): {text[:300]}")

                        if not check_valid_article(link, soup, title):
                            valid = check_valid_article(link, soup, title)
                            print(f"check_valid_article for {link}: {valid}")
                            if not valid:
                                print("Reasons:")
                                print(f"  - is_article_url: {is_article_url(link)}")
                                print(f"  - has_article_structure: {has_article_structure(soup)}")
                                print(f"  - has_long_title: {has_long_title(title)}")
                                print(f"  - title: {repr(title)}")

                            await article_page.close()
                            continue

                        published = None
                        try:
                            published = extract_published_date(soup)
                        except Exception:
                            pass

                        if published and published.year != 2025:
                            await article_page.close()
                            continue

                        if link.startswith("https://www.mckinsey.com") and report_filter(soup):
                            pdf_list.append(link)

                        if text:
                            results.append({
                                "url": link,
                                "title": title,
                                "content": text,
                                "published": published.isoformat() if published else None
                            })

                        self.visited_urls.add(link)

                    except Exception as e:
                        print(f"Error fetching article {link} with Playwright: {e}")
                    finally:
                        await article_page.close()

                await page.close()
                await browser.close()

        except Exception as e:
            print(f"Playwright Error for {url}: {e}")
            traceback.print_exc()
            return [], []

        return results, pdf_list

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

        if blocked_paths:
            if any(substr in path for substr in blocked_paths):
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
            pdf_list = []
            visited = set()

            # 1) fetch and parse main page data 
            if self.no_playwright(main_url): 
                title, text, soup = await self.fetch_html_async(session, main_url)

                if not soup:
                    return results, pdf_list

                # 2) extract article links directly from main page
                links = self.extract_links(main_url, soup)
                filtered_links = self.matcher.batch_match(links, keywords)

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
                    print(link)
                    title, text, soup = await self.fetch_html_async(session, link)
                    if (not soup or 
                        not check_valid_article(link, soup, title) or 
                        link.rstrip("/") == main_url.rstrip("/")):
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

                    results.append(
                        {
                            "url": link,
                            "title": title,
                            "content": text,
                            "published": published.isoformat() if published else None,
                        }
                    )

                    visited.add(link)
                    self.visited_urls.add(link)

            else:
                results, pdf_list = await self.fetch_playwright(main_url)

            return results, pdf_list
