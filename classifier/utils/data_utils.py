import os
import json
import pandas as pd

    
def join_json_data(folder_path: str, add_risk_col=False) -> pd.DataFrame:
    """ 
    Takes all json files and joins them into one
    
    Args:
        folder_path (str): Folder path to join files in
        add_risk_col (bool): To determine if label column should be added (Default: False)
    
    Returns: 
        pd.DataFrame: Dataframe of joined JSON files
    """
    df_all = pd.DataFrame()

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    file_df = pd.DataFrame(data)
                    df_all = pd.concat([df_all, file_df], ignore_index=True)

    if add_risk_col:
        df_all["risk"] = None  

    return df_all


def load_labelled_data() -> pd.DataFrame:
    """
    Loads all labelled training files and returns dataframe. Used for training model
    """
    folder_path = "../web_scraper/output/train_data/labelled_data/"
    labelled = join_json_data(folder_path)
    return labelled


def load_unlabelled_data() -> pd.DataFrame:
    """
    Loads all unlabelled files and returns dataframe to classify
    """
    folder_path = "../web_scraper/output/raw_results"
    unlabelled = join_json_data(folder_path, add_risk_col=True)
    return unlabelled