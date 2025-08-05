from typing import Tuple
from bs4 import BeautifulSoup
from newspaper import Article
from boilerpy3 import extractors

def clean_boilerplate(raw_text: str, html: str) -> str:
  """
  Cleans HTML using boilerplate
  
  Args:
    raw_text (str): The raw article text to fall back on if extraction fails
    html (str): The full HTML content of the article

  Returns:
    str: Cleaned article body text with boilerplate removed
  """
  extractor = extractors.ArticleExtractor()
  try:
    cleaned = extractor.get_content(html)
    return cleaned.strip() if cleaned else raw_text
  except Exception:
    return raw_text


def clean_newspaper(raw_text: str, html: str, url: str) -> str:
    """
    Use Newspaper to post-clean extracted article text.
     
    Args:
      raw_text (str): The raw article text to fall back on if extraction fails
      html (str): The full HTML content of the article

    Returns:
      str: Cleaned article body text extracted by Newspaper3k
    """
    article = Article(url=url)
    article.set_html(html)
    try:
        article.parse()
        return article.text.strip() if article.text else raw_text
    except Exception:
        return raw_text


def extract_clean_text(html: str, url: str, config: dict) -> Tuple[str, str]:
    """
    Extracts title and body text from an HTML page using config settings.

    Args:
        html (str): Raw HTML content.
        url (str): Article URL.
        config (dict): Config dict for this URL from urls.json.

    Returns:
        Tuple[str, str]: (title, body text)
    """
    
    soup = BeautifulSoup(html, "html.parser")
    
    method = config.get("method", "default")
    selectors = config.get("selectors", {})
    extractor_name = config.get("extractor", "")
    domain = config.get("domain", "")

    title, cleaned_text = "", ""
    
    if method == "newspaper":
        article = Article(url=url)
        article.set_html(html)
        try:
          article.parse()
          return article.title.strip(), article.text.strip()
        except Exception as e:
            print(f"Article extraction using Newspaper for {url} failed: {e}")
            return "", ""

    elif method == "custom" and extractor_name:
        extractor_func = EXTRACTOR_FUNCTIONS.get(extractor_name)
        if extractor_func:
          try: 
            title, raw_text = extractor_func(soup)
            cleaned_text = clean_newspaper(raw_text, html, url)
            return title, cleaned_text
          except Exception as e:
            print(f"Custom article extraction for Mckinsey failed: {e}. Passed to default")
            pass

    elif method == "boilerplate":
        title = extract_title(soup, selectors)
        raw_text = extract_body(soup, selectors, domain)
        cleaned_text = clean_boilerplate(raw_text, html)
        return title, cleaned_text

    else:
      if selectors: 
        title = extract_title(soup, selectors)
        raw_text = extract_body(soup, selectors, domain)
        cleaned_text = clean_newspaper(raw_text, html, url)
        return title, cleaned_text
      else:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        else:
            h1 = soup.find("h1")
            if h1 and h1.get_text(strip=True):
                title = h1.get_text(strip=True)
            elif soup.title and soup.title.string:
                title = soup.title.string.strip()
            else:
                title = ""
        
        # Extract body by joining all paragraphs on the page
        paragraphs = soup.find_all("p")
        lines = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        cleaned_text = "\n\n".join(lines)
        
        return title, cleaned_text
        
      
def extract_title(soup: BeautifulSoup, selectors: dict) -> str:
  """
  Extracts the title of an article from a BeautifulSoup-parsed HTML document.
  
  Args:
      soup (BeautifulSoup): Parsed HTML document.
      selectors (dict): Dictionary containing optional CSS selectors for the title.
          Expected format for title selector: ("tag_name", {"attr": "value"})

    Returns:
      str: The extracted title text, or an empty string if no title is found.
  """
  
  title_selector = selectors.get("title")
  if title_selector:
      tag, attrs = title_selector
      el = soup.find(tag, attrs)
      if el and el.get_text(strip=True):
        return el.get_text(strip=True)

  # Fallbacks
  og_title = soup.find("meta", property="og:title")
  if og_title and og_title.get("content"):
    return og_title["content"].strip()

  h1 = soup.find("h1")
  if h1 and h1.get_text(strip=True):
    return h1.get_text(strip=True)

  if soup.title and soup.title.string:
    return soup.title.string.strip()

  return ""

def extract_body(soup: BeautifulSoup, selectors: dict, domain: str) -> str:
  """
  Extracts the main body text of an article from a BeautifulSoup-parsed HTML document.
  
   Args:
      soup (BeautifulSoup): Parsed HTML document.
      selectors (dict): Dictionary containing optional CSS selectors for the article content
          Expected keys include "article_wrapper" and/or "article", each with ("tag", {attrs}) format
      domain (str): Domain of the article URL (used to skip certain domains in custom extraction)

    Returns:
        str: Extracted and cleaned body text of the article
  """
  article_html = None

  if "article_wrapper" in selectors:
    wrapper_tag, wrapper_attrs = selectors["article_wrapper"]
    wrapper = soup.find(wrapper_tag, wrapper_attrs)
    if wrapper and "article" in selectors:
      article_tag, article_attrs = selectors["article"]
      article_html = wrapper.find(article_tag, article_attrs)
  elif "article" in selectors:
    article_tag, article_attrs = selectors["article"]
    article_html = soup.find(article_tag, article_attrs)

  if article_html and domain not in {"mckinsey.com", "strategic-risk-global.com"}:
    paragraphs = article_html.find_all("p")
    lines = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    return "\n\n".join(lines)

  text = soup.get_text(separator="\n")
  lines = [line.strip() for line in text.split("\n") if line.strip()]
  return "\n".join(lines)

def extract_mckinsey_content(soup: BeautifulSoup) -> Tuple[str, str]:
  """
  Custom content extractor for mckinsey.com articles.

  Args:
      soup (BeautifulSoup): Parsed HTML content.

  Returns:
      str: Cleaned article body.
  """
  title_tag = soup.find("h1")
  title = title_tag.get_text(strip=True) if title_tag else ""
    
  article_div = soup.find("div", class_="mdc-o-content-body mck-u-dropcap")
  if not article_div:
      return title, ""

  lines = []
  for tag in article_div.find_all(["p", "h3"]):
      if tag.find_parent(class_=lambda c: c and (
          "DownloadsSidebar_" in c or
          "MostPopularArticles_" in c or
          "Table_" in c
      )):
          continue

      text = tag.get_text(strip=True)
      if not text:
          continue

      if tag.name == "h3":
          lines.append(f"\n\n**{text}**\n")
      else:
          lines.append(text)
  body = "\n\n".join(lines).strip()

  return title, body
    
# mapping mckinsey method
EXTRACTOR_FUNCTIONS = {
  "extract_mckinsey_content": extract_mckinsey_content
}