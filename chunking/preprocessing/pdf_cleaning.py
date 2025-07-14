from typing import List

def remove_footer_strings(text: str, footers: List[str]) -> str:
    """
    Remove any exact footer substrings from the text.
    """
    for footer in footers:
        text = text.replace(footer, "")
    return text

# ── Example ──────────────────────────────────────────────────────────

txt_path = 'chunking/raw_text/162raw.txt'
with open(txt_path, 'r', encoding='utf-8') as f:
    raw = f.read()

footers = [
    "PwC | Managing risk in higher education",

    "Internal Audit Hot Topics\n© 2023. For information, contact Deloitte Touche Tohmatsu Limited",

    "RESTRICTED DISTRIBUTION",
    "© 2023 Gartner, Inc. and/or its affiliates. All rights reserved. 779768",

    "12/18/23, 2:54 PM 2024 EDUCAUSE Top 10: Institutional Resilience | EDUCAUSE Review",
    "12/18/23, 2:54 PM",
    "https://er.educause.edu/articles/2023/10/2024-educause-top-10-institutional-resilience",

    "CONTENTS    I    1. BUDGET    I   2. STAFF    I   3. AUDIT PLANS    I   4. RISK LEVELS    I    5. LEADERSHIP METRICS",

    "protiviti.com \n|\n Executive Perspectives on Top Risks for 2024 and a Decade Later\n |\n\ erm.ncsu.edu"
]

cleaned = remove_footer_strings(raw, footers)
print(cleaned)
