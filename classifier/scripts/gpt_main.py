import pandas as pd
from classifier.model.chat4o_mini import classify_risk
from tqdm import tqdm
tqdm.pandas()

def gpt_main(data: pd.DataFrame) -> pd.DataFrame: 
  """
  Performs GPT classification and only returns risk-event dataframe
  """
  
  data["risk"] = data["cleaned_text"].progress_apply(
        lambda text: 1 if classify_risk(text).lower() == "true"
        else 0 if classify_risk(text).lower() == "false"
        else -1
    )

  num_errors = (data["risk"] == -1).sum()
  if num_errors > 0:
      print(f"Warning: {num_errors} rows had classification errors")

  positives_df = data[data["risk"] == 1].copy()
  print(f"{len(positives_df)} samples predicted as risk-event.")

  return positives_df