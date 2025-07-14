from typing import List

def remove_footer_strings(text: str, footers: List[str]) -> str:
    """
    Remove any exact footer substrings from the text.
    """
    for footer in footers:
        text = text.replace(footer, "")
    return text


# ── Example ──────────────────────────────────────────────────────────

raw = ""

footers = [
    "PwC | Managing risk in higher education",
    "© 2023. For information, contact Deloitte Touche Tohmatsu Limited",
    


    "protiviti.com \n|\n Executive Perspectives on Top Risks for 2024 and a Decade Later\n |\n\ erm.ncsu.edu"
]

cleaned = remove_footer_strings(raw, footers)
print(cleaned)
