# test_model_analysis.py

import json
from models.previous_model import web_articles  # make sure this is correct

def load_test_article(filepath: str): 
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def test_model_analysis():
    articles = load_test_article("data/filtered_results/filtered_ctvnews_20250617_093047.json")
    filename = "data/test_analysis_results/filtered_ctvnews_20250617_093047_analysis.json"
    
    article_results = []  
    
    for article in articles:
      content = article.get("content", "")
      result = web_articles(content)
      article_results.append(result)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(article_results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    test_model_analysis()
    print("Model analysis completed and saved.")
