from newspaper import Article

def fetch_article_newspaper(url):
    article = Article(url)
    article.download()
    article.parse()
    title = article.title
    text = article.text
    return title, text

# Example usage:
url = "e"  # Replace with real article URL
title, text = fetch_article_newspaper(url)
print("Title:", title)
print("Content preview:", text[:500])  # print first 500 chars
