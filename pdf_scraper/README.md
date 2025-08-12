# PDF Scraper 
This folder contains the files to run pdf scrapping. It takes pdfs and returns a clean text file.  

## Folder Structure 
```
├── outputs/                                          # Stores outputs (clean text files)
|                      
├── scripts/                                          # PDF scraping scripts
│   ├── pdf_scraping.py                               # Main script for pdf scraping
├── utils/
│   ├── chunking.py                                   # Implements chunking by heading (archived)
│   ├── table_of_contents.py                          # Identifies TOC and used in chunking (archived)
│   ├── text_preprocessing.py                         # Basic text preprocessing (archived - added to main script)
|
├── chunking                                          # Exhaustive list of chunking methods explored
```

## Workflow
1. Gathers raw pdf files from data/input/pdfs. 
2. Runs pdf_scraping.py where:
  - Text is extracted using PyMuPDF
  - If page includes minimal text, then OCR extracts information instead
  - Text is cleaned (e.g., remove page numbers, special characters, etc.)
  - Unique footers removed
  - First and last page removed
  - Information about TOC for chunking is gathered bu commented out due to this process no longer being part of pipeline. 
3. Outputs clean text files in pdf_scraping/outputs 