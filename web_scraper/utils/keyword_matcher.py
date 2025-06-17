# utils/keyword_matcher.py 

from sentence_transformers import SentenceTransformer, CrossEncoder, util
from typing import List, Dict

class KeywordMatcher: 
  def __init__(self, threshold: float = 0.2, 
               cosine_name: str = "all-MiniLM-L6-v2",
               cross_name: str = "cross-encoder/stsb-roberta-large",
               fallback_min: float = 0.15, 
               fallback_max: float = 0.35):
    """
    Initialize KeywordMatcher with sentence embedding model

    Args:
      threshold (float): Similarity threshold for matching
      cosine_name (str): Name of sentence-transformers model used
      cross_name (str): Name of cross-encoder model used 
      fallback_min (float): Cosine lower-bound to consider fallback
      fallback_max (float): Cosine upper-bound to consider fallback
    """

    self.threshold = threshold
    self.fallback_min = fallback_min
    self.fallback_max = fallback_max

    self.cosine_model = SentenceTransformer(cosine_name)
    self.cross_encoder = CrossEncoder(cross_name)

  def batch_match(self, link_dict: Dict, keywords: List[str]) -> Dict:
    """
    For each title sourced from main URL, perform cosine similarity to only crawl relevant links

    Args:
      link_dict (dict): Dictionary of links and corresponding titles from main URL 
      keywords (List[str]): List of keywords for the respective URL to restrict search 

      Returns: 
        Dict: filtered dictionary of relevant links and titles to crawl
    """

    if not link_dict:
      return {}
    
    if not keywords:
      return link_dict
    
    urls = list(link_dict.keys())
    titles = list(link_dict.values())

    title_embeddings = self.cosine_model.encode(titles, convert_to_tensor=True)
    keyword_embeddings = self.cosine_model.encode(keywords, convert_to_tensor=True)

    cosine_scores = util.cos_sim(title_embeddings, keyword_embeddings)

    filtered_dict = {}
    for i, url in enumerate(urls):
      title = titles[i]
      max_cosine_score = cosine_scores[i].max().item()
      # print(f"[DEBUG] Title: {title}\n[DEBUG] Max Score: {max_cosine_score:.4f}")
      if max_cosine_score >= self.threshold:
        filtered_dict[url] = title
      
      elif self.fallback_min <= max_cosine_score <= self.fallback_max:
        # Re-scoring evaluation with CrossEncoder Model 
        pairs = [(keyword, title) for keyword in keywords]
        ce_scores = self.cross_encoder.predict(pairs)
        max_ce_scores = max(ce_scores)
        normalized_ce_score = max_ce_scores/5
        # print(f"[DEBUG] Title: {title}\n[DEBUG] Max Score: {normalized_ce_score:.4f}")
        if normalized_ce_score >= self.threshold:
          filtered_dict[url] = title
      
    return filtered_dict
