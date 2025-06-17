# content_cleaner.py

from typing import List, Dict
from readability import Document
from bs4 import BeautifulSoup

def content_cleaner(raw_results: List[Dict]) -> List[Dict]:
  """
  Takes raw results for each site and cleans up output to increase readability 

  Args:
    raw_results (List[Dict]): Content saved from web scrape 

  Returns:
    List[Dict]: Returns clean content in same format as input  
  """
  clean_results = []
  for page in raw_results: 
    content = page.get("content", "")
    clean_content = body_extraction(content)

    if clean_content: 
      clean_results.append({
        "url": page.get("url", ""),
        "title": page.get("title", ""),
        "clean_content": clean_content,
        "published": page.get("published", "")
      }
      )

  return clean_results

def body_extraction(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    main_container = (soup.find('div', class_='detailBodyContainer') 
                      or soup.find('article') 
                      or soup.find('main'))

    if not main_container:
        print("No main container found, falling back to full HTML")
        main_container = soup
    else:
        print(f"Found main container: {main_container.name} with classes {main_container.get('class')}")

    for tag in main_container(['script', 'style', 'nav', 'footer', 'aside', 'header', 'form', 'iframe']):
        tag.decompose()

    paragraphs = main_container.find_all('p')
    print(f"Found {len(paragraphs)} paragraphs")

    article_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    
    if not article_text:
        print("No paragraph text extracted!")

    return article_text
