import unittest
from utils.keyword_matcher import KeywordMatcher

class TestKeywordMatcher(unittest.TestCase):

  def setUp(self):
    # Initialize KeywordMatcher
    self.matcher = KeywordMatcher()

  def test_keyword_match_relevant(self):
    link_dict = {
      "https://example.com/flooding": "Flooding has increased due to climate change",
      "https://example.com/wildfire": "Thousands evacuated due to Kelowna wildfires",
      "https://example.com/mlb": "Today's MLB Highlights"
    }

    keywords = ["extreme weather", "risk"]

    filtered = self.matcher.batch_match(link_dict, keywords)
    self.assertIn("https://example.com/flooding", filtered)
    self.assertIn("https://example.com/wildfire", filtered)
    self.assertNotIn("https://example.com/mlb", filtered)

  def test_keyword_match_no_keywords(self):
    link_dict = {"https://example.com":"Title"}
    keywords = []
    filtered = self.matcher.batch_match(link_dict, keywords)
    self.assertEqual(filtered, link_dict)

  def test_keyword_match_no_links(self):
    link_dict = {}
    keywords = ["extreme_weather"]
    filtered = self.matcher.batch_match(link_dict, keywords)
    self.assertEqual(filtered, {})

  def test_keyword_match_irrelevant(self):
    link_dict = {"https://example.com/news": "Canadian Politics"}
    keywords = ["extreme weather"]
    filtered = self.matcher.batch_match(link_dict, keywords)
    self.assertEqual(filtered, {})

if __name__ == "__main__":
    unittest.main()