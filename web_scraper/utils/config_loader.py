# utils/config_loader.py

import json
from urllib.parse import urlparse

def load_url_config(filepath: str) -> dict:
    """
    Loads the settings for each URL.

    Args:
        filepath (str): Path to the JSON file with URL configurations.

    Returns:
        dict: Dictionary of configuration settings keyed by start URL.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Add domain to each config entry
    for start_url, settings in config.items():
      parsed = urlparse(start_url)
      domain = parsed.netloc
      if domain.startswith("www."):
          domain = domain[4:]  
      settings["domain"] = domain
      
    return config

if __name__ == "__main__":
  config = load_url_config()
