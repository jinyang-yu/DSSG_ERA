import fitz
import os
from project.utils.text_processing import clean_text
import pytesseract
from pdf2image import convert_from_path

def extract_text_text(pdf_path, folder_path):
    doc = fitz.open(f'{folder_path}{pdf_path}')
    pdf_text = ""
    for page in doc:
        pdf_text += page.get_text()

    return pdf_text


def extract_text_ocr(pdf_path, folder_path):
    try:

        images = convert_from_path(f'{folder_path}{pdf_path}')
        ocr_text = ""

        for i, image in enumerate(images, start=1):
            
            ocr_text += pytesseract.image_to_string(image)

        return ocr_text.strip()
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return ""
    

def is_pdf_image_based(pdf_path, folder_path):
    """
    Determine if a PDF is image-based or text-based by analyzing text and image content.
    """
    texts = []
    with fitz.open(f'{folder_path}{pdf_path}') as doc:
        for page in doc:
            # Extract and clean text
            text = page.get_text()
            cleaned_text = clean_text(text)
            texts.append(cleaned_text)

        texts = " ".join(texts)

            # Check for substantial text

        if len(texts) > 1500:  # Threshold for "meaningful" text
            print('text-based')
            return False  # The PDF has substantial text
        else:
            print('image-based')
            return True

def read_pdf(pdf_path, folder_path):
    if is_pdf_image_based(pdf_path, folder_path):
        return extract_text_ocr(pdf_path, folder_path)
    else:
        return  extract_text_text(pdf_path, folder_path)



