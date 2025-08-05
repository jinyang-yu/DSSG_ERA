# utils/article_filter.py 
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from urllib.parse import urlparse
from htmldate import find_date
from typing import List, Optional

def is_url_blocked(url: str, config: dict) -> bool: 
    """
    Checks if the URL is blocked in utils/site_rules.py to avoid unnecessary scraping 

    Args:
      url (str): URL to check if adheres to configured site_rules.py 
      config (dict): config dictionary of corresponding URL

    Returns:
      bool: True if URL blocked according to site_rules.py
    """

    parsed = urlparse(url)
    path = parsed.path.lower() or "/"

    blocked_paths = config.get("blocked_paths", [])
    allowed_paths = config.get("allowed_paths", [])

    if blocked_paths:
        if any(substr in path for substr in blocked_paths):
            return True

    if allowed_paths:
        if not any(substr in path for substr in allowed_paths):
            return True

    else:
      return False

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
      
  date_span = soup.find("span", class_="u-meta-date u-meta-icon")
  if date_span:
      date_text = date_span.get_text(strip=True)
      try:
          return date_parser.parse(date_text)
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

def extract_all_published_dates(soup: BeautifulSoup) -> List[datetime]:
  """
  Extracts all publish dates from the given HTML soup, prioritizing <article> tags.
  
  Args:
    soup (BeautifulSoup): Parsed HTML content of a page

    Returns:
      List[datetime]: A list of datetime objects representing all found publish dates
  """
  dates = []
  articles = soup.find_all('article')
  if not articles:
    time_tags = soup.find_all("time", {"datetime": True})
    for tag in time_tags:
      try:
        dt = datetime.fromisoformat(tag["datetime"])
        dates.append(dt)
      except Exception:
        continue
  else:
    for article in articles:
      dt = extract_published_date(article)
      if dt:
        dates.append(dt)
        
  return dates

def report_filter(soup: BeautifulSoup) -> bool: 
  """
  Detects if report for Mckinsey & Company to save & export PDF manually (for now)

  Args:
    soup (BeautifulSoup): HTML content to check 
  
  Returns: 
    bool: True if Mckinsey's report
  """

  meta = soup.find("meta", attrs={"name": "searchresults-tags"})
  if meta and "| Report |" in meta.get("content", ""):
    return True




