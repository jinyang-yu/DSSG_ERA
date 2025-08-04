from utils import data_utils, data_cleaner
from scripts.catboost_main import catboost_main
from scripts.gpt_main import gpt_main
from datetime import datetime

def main():
  """
  Main script for classification. Currently configured for GPT-version
  """
  # Retrieving data and cleaning
  data = data_utils.load_unlabelled_data()
  data = data.drop_duplicates(subset="url")
  data["cleaned_text"] = data.apply(lambda row: data_cleaner.content_cleaner(row["content"], row["url"]), axis=1)
  
  print(f"Retrieved len{data} to classify")
  
  # to run GPT classification 
  print("Starting GPT Classification")
  risk_labelled_data = gpt_main(data)
  
  # to run catboost classification 
  # print("Starting Catboost Classification")
  # risk_labelled_data = catboost_main(data)
  
  # Change path accordingly
  date_str = datetime.now().strftime("%Y-%m-%d")
  filename = f"data/risk_events_{date_str}.json"
  risk_labelled_data.to_json(filename, orient="records", lines=False, indent=2)
  
  
if __name__ == "__main__":
    main()