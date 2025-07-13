# test_filter_content.py

import json
from utils.article_filter import filter_content

with open ("data/raw_results/mckinsey_20250702.json", "r", encoding="utf-8") as f:
  raw_data = json.load(f)

print(f"loaded {len(raw_data)} raw items.")

filtered_data = filter_content(raw_data)

print(f"{len(filtered_data)} items after filtering")

with open ("data/filtered_results/filtered_mckinsey_20250702.json", "w", encoding="utf-8") as f:
  json.dump(filtered_data, f, indent=2, ensure_ascii=False)

print("Filtered results saved")