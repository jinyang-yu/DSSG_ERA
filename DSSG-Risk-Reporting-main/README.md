# Risk Analysis System: Data Flow and Logic Explanation

## Overview
This system is designed to extract, process, and analyze risk information from PDF reports. It uses AI models to identify and structure key risks, their drivers, recommendations, trends, and other related data from various risk reports.

## Data Flow

### 1. PDF Input Handling
- PDFs are read from the 'data/' directory
- The system distinguishes between long PDFs (>60 pages) and short PDFs
- Each PDF is processed based on its length using different approaches

### 2. Short PDF Processing
- For short PDFs (<60 pages):
  - The entire PDF text is extracted using the `read_pdf` function
  - The function determines if the PDF is image-based or text-based and uses the appropriate extraction method
  - The text is sent directly to the OpenAI API using the `short_pdfs` function
  - Results are saved to the "project/results/" directory

### 3. Long PDF Processing
- For long PDFs (>60 pages), a more complex process is used:
  
  a. **Table of Contents Extraction**:
  - The system locates the table of contents page
  - This page is saved as an image and encoded to base64
  - The image is sent to the OpenAI API (GPT-4o) via `table_contents_f` function
  - The API returns a structured JSON with sections and their page ranges
  - Page numbering corrections are applied if needed

  b. **Section Processing**:
  - Relevant sections are extracted based on the table of contents
  - Footer text is cleaned from the sections
  - Sections are combined based on token count (to stay within API limits)
  - Key highlights section (if present) is processed separately

  c. **AI Analysis**:
  - For key highlights, the system uses `key_insights` function with GPT-4o-mini
  - For other sections, the system uses `long_pdfs` function with O3-mini
  - Final results are combined using the `join_dicts` function

### 4. Output Generation
- The analysis results are saved as JSON files in the "project/results/" directory
- Each output contains structured risk information including:
  - Risk Name
  - Risk Description
  - Risk Driver (list of drivers and descriptions)
  - Risk Recommendations
  - Trend
  - Likelihood
  - Impact
  - Risk Indicator
  - Risk Event
  - Contextual Variations

## Key Components

### 1. PDF Utility Functions (`pdf_utils.py`)
- Handles PDF text extraction using different methods
- Determines if PDFs are image-based or text-based
- Uses OCR for image-based PDFs and direct text extraction for text-based PDFs

### 2. Text Processing (`text_processing.py`)
- Cleans and normalizes extracted text
- Removes page numbers, special characters, and formatting
- Fixes common OCR errors and normalizes spacing

### 3. AI Models
- **chat4o_image.py**: Uses GPT-4o to process table of contents images
- **chat_mini.py**: Uses GPT-4o-mini to analyze key insights sections
- **o3_mini.py**: Uses Anthropic's O3-mini model to analyze full sections and join results

### 4. Risk Processing Logic (`risks.py`)
- Core orchestration file that manages the entire process flow
- Contains functions for PDF classification, text extraction, and AI integration
- Handles section division, combination, and result storage

## Risk Analysis System Architecture

```
PDF Documents → PDF Classification → 
  ├── Short PDFs → Direct Text Extraction → AI Risk Analysis
  └── Long PDFs → Table of Contents Extraction → Section Extraction → 
                   Section Combination → Multiple AI Analysis Passes → 
                   Results Combination
```

## Why This Approach
- Split processing allows handling of different PDF types effectively
- Using the table of contents to extract relevant sections increases efficiency
- Processing sections separately helps stay within token limits
- Different AI models are used for different tasks based on their strengths
- The system tracks processed PDFs to avoid redundant processing

This approach enables comprehensive risk analysis from varied source documents while maintaining scalability and accuracy.