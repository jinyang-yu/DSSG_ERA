# utils/article_filter.py 
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from urllib.parse import urlparse
from htmldate import find_date
from typing import Optional

UNWANTED_SUBSTRINGS = [
    "tag", "author", "about", "contact", "team", "cookie",
    "terms", "login", "signup", "feed", "subscribe", "advertise", "search",
    "page", "wp-", "admin", "sitemap", "donate", "sample"
]

def is_article_url(url: str) -> bool:
  """
  Initially checking that URL does not contain any unwanted substrings that are indicators of non-article

  Args:
    url (str): URL to evaluate 

  Returns:
    bool: True if URL has no unwanted substring
  """
  path = urlparse(url).path.lower()
  segments = [segment for segment in path.split("/") if segment]
  return not any(seg in UNWANTED_SUBSTRINGS for seg in segments)

def has_article_structure(soup: BeautifulSoup) -> bool:
  """
  Checks presence of specific HTML elements that are typically found in article URLs

  Args:
    soup (BeautifulSoup): Parsed HTML soup

  Returns:
    bool: True if article-like elements present
  """

  return bool(
    soup.find("article") or
    soup.find("time") or
    soup.find("meta", attrs={"property": "article:published_time"}) or
    soup.find("div", class_="article-content") or
    soup.find("div", class_="post-content")
  )

def has_long_title(title: str) -> bool:
  """
  Checks if title of link is likely an article (> 2 words)

  Args:
    title (str): title of link 

  Returns: 
    bool: True if likely article title
  """

  if not title: 
    return False
  
  return len(title.split()) > 2

def check_valid_article(url: str, soup: BeautifulSoup, title: str, min_conditions: int = 2) -> bool:
  """
  Checks all 3 conditions on article likelihood to restrict content scraping 

  Args:
    url (str): URL to scrape
    soup (BeautifulSoup): Parsed HTML soup
    title (str): title of URL

  Returns: 
    bool: True if likely article
  """ 

  checks = [
    is_article_url(url), 
    has_article_structure(soup), 
    has_long_title(title)
  ]

  return sum(checks) >= min_conditions

def extract_published_date(soup: BeautifulSoup) -> Optional[datetime]:
  """
  Finds and extracts published date on page data

  Args: 
    soup (BeautifulSoup): Parsed HTML soup

  Returns:
    datetime or None: datetime of publish if exists
  """

  time_tag = soup.find("time", {"datetime": True})
  if time_tag:
    try:
      return datetime.fromisoformat(time_tag["datetime"])
    except Exception:
      try:
        return date_parser.parse(time_tag["datetime"])
      except Exception:
        pass
  
  html = soup.decode()
  if html: 
    try: 
      date_str = find_date(html)
      if date_str:
        return datetime.fromisoformat(date_str)
    except Exception: 
      pass

  return None

