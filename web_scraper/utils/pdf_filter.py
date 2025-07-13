# pdf_filter.py

import os
import requests 
from bs4 import BeautifulSoup

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