# utils/url_tracker.py

import json
from typing import Set, Dict

def load_visited(filepath: str) -> Set:
  """
  Load visited URLs from a stored JSON file in previous execution

  Args:
    filepath (str): filepath of JSON URL file 

  Returns:
    Set: set of URLs that were previously visited
  """

  try: 
    with open(filepath, "r") as f:
      return set(json.load(f))
  except (FileNotFoundError, json.JSONDecodeError):
    return set()
  
def save_visited(visited: Set[str], filepath: str):
  """
  Saves updated version of visited URL file from current execution 

  Args: 
    visited (set): Updated set of visited URLs (previous and new)
    filepath (str): Filepath of JSON URL file
  """

  with open(filepath, "w", encoding = "utf-8") as f:
    json.dump(sorted(visited), f, indent=2)

def load_urls(filepath: str) -> Dict:
  """
  Load URLs to scrape and the respective keywords to restrict search to

  Args:
    filepath (str): Path to JSON file containing information on URLs to scrape 

  Returns:
    List[Dict]: Dictionary mapping each URL to search keywords. Returns empty if error.

  """

  try:
    with open(filepath, "r") as f:
      data = json.load(f)
      if isinstance(data, Dict):
        return data
      else:
        print(f"Warning: Expected dict in {filepath} but got {type(data)}")
      
  except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading {filepath}: {e}")
    return []