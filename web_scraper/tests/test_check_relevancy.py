# test_4o_filter.py
from models.content_filter import check_relevancy
import json

def load_test_article(filepath: str): 
  with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

  return data

def test_mixed_articles():
  articles = load_test_article("data/raw_results/universityaffairs_20250617_092934_new.json")

  expected = ["True"]
  actual = []
  
  for i, article in enumerate(articles):
    content = article.get("content", "")
    assert isinstance(content, str) and content.strip(), f"Article {i} is invalid"

    result = check_relevancy(content)
    actual.append(result)

  assert expected == actual


  
