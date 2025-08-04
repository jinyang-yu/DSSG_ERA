import re
from urllib.parse import urlparse
from .domain_patterns import DOMAIN_PATTERNS


def content_cleaner(content: str, url: str = None) -> str:
    """
    Clean raw article text extracted from various sites, removing domain-specific boilerplate and noise,
    while preserving line breaks.
    
    Args:
        content (str): Raw content from file to clean
        url (str): URL of corresponding content
    
    Returns: 
        str: Cleaned version of content
    """
    text = content
    domain = None

    if url:
        try:
            domain = urlparse(url).netloc.lower()
        except Exception:
            domain = None

    if domain and domain in DOMAIN_PATTERNS:
        patterns = DOMAIN_PATTERNS[domain]
        lines = text.splitlines()
        filtered_lines = []
        for line in lines:
            stripped_line = line.strip()
            if any(re.search(pattern, stripped_line, re.IGNORECASE) for pattern in patterns):
                continue
            if stripped_line: 
                filtered_lines.append(stripped_line)
        text = "\n".join(filtered_lines)

    else:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

    return text