import json

filepath = 'data/train_data/enterpriseriskmag_20250721_train.json'

with open(filepath, 'r') as f:
    data = json.load(f)  # should be a list of dicts
    print(f"Number of entries: {len(data)}")
