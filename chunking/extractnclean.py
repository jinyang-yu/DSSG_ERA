import pdfplumber
import re

def pdf_to_text(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text())
    return "\n".join(filter(None, text))

raw_text = pdf_to_text("./data/higher-education-sector-risk-profile-2023.pdf")

# Write the raw text to a file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(raw_text)
print("\nText has been saved to 'output.txt'")

## Clean the text
def clean_text(text: str) -> str:
    # remove page numbers
    text = re.sub(r'\b(page|pg)\.?\s*\d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE) 
    
    # remove special characters and formatting (bullet points, control characters)
    text = re.sub(r'[•●■□▪▫]', '', text) 
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\xFF]', '', text)  
    
    # remove footer/header patterns (dates, page numbers)
    text = re.sub(r'^\s*\d+\s*of\s*\d+\s*$', '', text, flags=re.MULTILINE)  
    text = re.sub(r'^\s*\d{1,2}/\d{1,2}/\d{2,4}\s*$', '', text, flags=re.MULTILINE)  
    
    # remove extra whitespace and normalize spaces
    text = re.sub(r'\s+', ' ', text) 
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE) 
    
    # remove empty lines
    text = '\n'.join(line for line in text.splitlines() if line.strip())
    
    # remove repeated punctuation
    text = re.sub(r'([.,!?])\1+', r'\1', text)

    # normalize Unicode dashes to standard dash
    text = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015]', '-', text)

    # normalize quotes
    text = re.sub(r'[''´`]', "'", text)
    text = re.sub(r'["""]', '"', text)

    # fix common OCR errors
    text = re.sub(r'\bI(?=[a-z]{2,})\b', 'l', text)

    # fix spacing around punctuation
    text = re.sub(r'\s+([.,!?:;])', r'\1', text)
    text = re.sub(r'(\d)\s+%', r'\1%', text) 
    
    # remove any remaining double spaces
    text = ' '.join(text.split())
    
    return text.strip()

clean_text= clean_text(raw_text)

with open("cleaned_output.txt", "w", encoding="utf-8") as f:
    f.write(clean_text)
print("\nCleaned text has been saved to 'cleaned_output.txt'")

