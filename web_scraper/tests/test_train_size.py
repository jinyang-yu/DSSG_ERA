import json

filepath = 'data/raw_results/ctvnews_20250723_rerun.json'

with open(filepath, 'r') as f:
    data = json.load(f)  # should be a list of dicts
    print(f"Number of entries: {len(data)}")
