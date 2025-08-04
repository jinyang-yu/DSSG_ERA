from catboost import CatBoostClassifier
from sentence_transformers import SentenceTransformer
import pandas as pd

  
def catboost_main(data: pd.DataFrame) -> pd.DataFrame:
  """
  Runs catboost classification model on data, returning risk-event data only
  """
  
  # Loading and using model
  model = CatBoostClassifier()
  model.load_model("model/catboost_model.cbm")
  
  texts = data["cleaned_text"].tolist()
  embedder = SentenceTransformer('all-MiniLM-L6-v2')
  X_embed = embedder.encode(texts, batch_size=32, show_progress_bar=True)
  
  # Predict probabilities
  threshold = 0.19
  probs = model.predict_proba(X_embed)[:, 1]
  preds = (probs > threshold).astype(int)
  
  # Filter for positive rows 
  data["risk"] = preds

  # Filter only positive predictions
  positives_df = data[data["risk"] == 1].copy()
  print(f"{len(positives_df)} samples predicted as risk-event")
  
  return positives_df


if __name__ == "__main__":
  catboost_main()