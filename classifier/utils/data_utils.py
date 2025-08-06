import os
import json
import pandas as pd

def load_classified_files(path=str) -> set:
    if os.path.exists(path):
        with open(path, "r") as f:
            return set(json.load(f))
    return set()

def save_classified_files(classified_set: set, path=str):
    with open(path, "w") as f:
        json.dump(sorted(classified_set), f, indent=2)
    
def join_json_data(folder_path: str, add_risk_col=False, classified_path="classifier/classified.json") -> pd.DataFrame:
    """ 
    Takes all json files and joins them into one
    
    Args:
        folder_path (str): Folder path to join files in
        add_risk_col (bool): To determine if label column should be added (Default: False)
    
    Returns: 
        pd.DataFrame: Dataframe of joined JSON files
    """
    df_all = pd.DataFrame()
    classified = load_classified_files(classified_path)
    newly_classified = set()

    for filename in os.listdir(folder_path):
        if filename.endswith(".json") and filename not in classified:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    file_df = pd.DataFrame(data)
                    df_all = pd.concat([df_all, file_df], ignore_index=True)
                    newly_classified.add(filename)

    save_classified_files(classified.union(newly_classified), classified_path)
    
    if add_risk_col:
        df_all["risk"] = None  

    return df_all


def load_labelled_data() -> pd.DataFrame:
    """
    Loads all labelled training files and returns dataframe. Used for training model
    """
    folder_path = "web_scraper/output/train_data/labelled_data/"
    labelled = join_json_data(folder_path)
    return labelled


def load_unlabelled_data() -> pd.DataFrame:
    """
    Loads all unlabelled files and returns dataframe to classify
    """
    folder_path = "web_scraper/output/raw_results"
    unlabelled = join_json_data(folder_path, add_risk_col=True)
    return unlabelled