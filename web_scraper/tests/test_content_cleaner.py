import json
import os
from utils.content_cleaner import content_cleaner  # adjust the import to where your cleaner lives

def test_cleaner_on_raw_file(raw_file_path):
    with open(raw_file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Apply your cleaner
    cleaned_data = content_cleaner(raw_data)

    # Save to corresponding clean file
    base_name = os.path.basename(raw_file_path).replace(".json", "_clean.json")
    clean_path = os.path.join("data/clean_results", base_name)

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"Cleaned content saved to: {clean_path}")


if __name__ == "__main__":
    # Example file — replace this with any raw result you want to test
    test_cleaner_on_raw_file("data/raw_results/cbc_20250617_102753.json")
