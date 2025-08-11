# Classifier
This folder contains the contents for the binary classifier to detect risk-related events.

## Folder Structure
```
├── model/                       
│   ├── catboost_model.cbm         # Saved CatBoost classification model
│   ├── chat4o_mini.py             # Prompt for the GPT-classification version    
│
├── output/                        # Main results folder for classifier
│   ├── archives/                  # Archives folder for previous runs
│
├── scripts/                       # All scripts to instantiate various parts of the workflow
│   ├── catboost_main.py           # Script for CatBoost model version
│   ├── classifier_matrix.py       # Generates confusion matrix and classification report (purpose: assess performance)
│   ├── classifier_trainer.py      # Script used to train CatBoost classification model
│   ├── gpt_main.py                # Main script for running GPT 4o-mini classifier version
│
├── utils/
│   ├── data_cleaner.py            # Cleans text through REGEX for specified patterns in content
│   ├── data_utils.py              # Loads, saves, joins all labelled/unlabelled data for CatBoost
│   ├── domain_patterns.py         # Stores specific boilerplate patterns in esgtoday.com and universityworldnews.com to remove
│
├── run_classifier.py              # Main file to run classifier model
├── classified.json                # Keeps track of website files that were already run through and classified
```

## Classifier Versions 
This project includes **two versions** of the classifier, where version 1 is the base configuration

### **Version 1 - GPT Classifier**
The base version leverages the GPT 4o-mini model to prompt and detect if the article is classified as "risk-event" or not. The input of the prompt is the cleaned_text column 

### **Version 2 - CatBoost Classifier**
This version was experimented to incorporate an encoder-only approach in the pipeline, to highlight the various strengths of implementing this type of model in a data science workflow. 

The CatBoost model lacks strong quality training data, and thus if this approach is considered in the future, re-training on more labelled data by domain experts is essential. The current model is trained on a sample size of ~225 labelled data and is built on the semi-supervised learning approach, with confidence of 0.95 for pseudo-labels and 25 max predictions added to training each iteration.  

**How to Run Version 2**

In run_classifier.py, comment out gpt_main, and uncomment out the line for catboost_main:
```Python 
# to run GPT classification 
# risk_labelled_data = gpt_main(data)

# to run catboost classification 
risk_labelled_data = catboost_main(data)
```
## Results 
The articles that were classified as "risk" and passsed through the filter, is under *risk_events_date.json* in output/. 

The file is of the same format as the web-scraped json file content, however it contains all articles from all sources that were included in the specific iteration. It has additional keys under "risk" for the binary output from the classification model and "cleaned_text", that is the cleaned up article content with boilerplate removed.

