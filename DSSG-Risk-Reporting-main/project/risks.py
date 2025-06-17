import fitz
import os
import pdfplumber
import base64
from pypdf import PdfReader
import re
import json
from project.models.chat_mini import key_insights
from project.models.o3_mini import short_pdfs, long_pdfs, join_dicts
from project.models.chat4o_image import table_contents_f
from project.utils.pdf_utils import read_pdf
import openai
from openai import OpenAIError
import time

folder_path = 'data/test/'
output_dir_default = "project/results/"
table_contents_dir = "project/table_content/images/"
dict_table_contents_dir = "project/table_content/dictionaries/"
pdf_sections_dir = "project/sections/pdf_sections/"
combinations_dir = "project/sections/combinations/"

def clean_text_footers(text, common_footers):
    text = re.sub(r"\b\d{1,3}\b\s*$", "", text)
    text = re.sub(r"(Figure\s\d+\.\d+|Source:.*|F I G U R E.*)", "", text, flags=re.IGNORECASE)
    for footer in common_footers:
        text = text.replace(footer, "")
    return text.strip()

def save(pdf_name, dir, content):
    os.makedirs(dir, exist_ok=True)
    with open(os.path.join(dir, f'{pdf_name}.json'), 'w') as f:
        json.dump(content, f)
    print(f"✅ Saved result to {os.path.join(dir, f'{pdf_name}.json')}")

def is_pdf_long(pdf_path):
    doc = fitz.open(f'{folder_path}{pdf_path}')
    return len(doc) > 60

def send_short(pdf_path):
    text = read_pdf(pdf_path, folder_path)
    print('send_short accessed')
    result = short_pdfs(text)
    save(pdf_path, output_dir_default, result)
    return result

def find_toc_page(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and ("Table of Contents" in text or "Contents" in text or "CONTENTS" in text): 
                return i
    return None

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_string}"

def save_toc_page_as_image(pdf_path, page_number, output_image_path):
    doc = fitz.open(pdf_path)
    page = doc[page_number]
    pix = page.get_pixmap(dpi=300)
    pix.save(output_image_path)
    doc.close()

def process_pdf_toc(pdf_path, table_contents_dir, pdf):
    toc_page = find_toc_page(pdf_path)
    if toc_page is None:
        print(f"No Table of Contents found in {pdf_path}")
        return
    print(f"TOC found on Page {toc_page + 1} in {os.path.basename(pdf_path)}")
    output_image_path = os.path.join(table_contents_dir, f"{pdf}.png")
    save_toc_page_as_image(pdf_path, toc_page, output_image_path)
    return encode_image_to_base64(output_image_path)

def get_difference(pdf):
    count = 0
    reader = PdfReader(f"{folder_path}{pdf}")
    for index, page in enumerate(reader.pages):
        if count == 0:
            pg = int(reader.page_labels[index])
            if pg > 1:
                count += 1
                diff = abs(int(reader.page_labels[index]) - (index + 1))
                return diff
    return 0

def detect_common_footer(text_list):
    from collections import Counter
    footer_candidates = Counter(text_list)
    return {text for text, count in footer_candidates.items() if count > 1 and len(text) < 100}

def extract_text(page_range):
    extracted_texts = []
    footer_candidates = []
    for page in range(page_range[0] - 1, page_range[1]):
        raw_text = doc[page].get_text("text").strip()
        lines = raw_text.split("\n")
        if len(lines) > 2:
            footer_candidates.append(lines[-1])
            footer_candidates.append(lines[-2])
        extracted_texts.append(raw_text)
    common_footers = detect_common_footer(footer_candidates)
    cleaned_text = [clean_text_footers(text, common_footers) for text in extracted_texts]
    return " ".join(cleaned_text)

def send_table_contents(pdf):
    pdf_path = f'{folder_path}{pdf}'
    n = find_toc_page(pdf_path)
    if n is not None:
        base64_image = process_pdf_toc(pdf_path, table_contents_dir, pdf)
        response = call_openai(table_contents_f, base64_image)
        print('table of contents back from api')
        diff = get_difference(pdf)
        if diff > 0:
            for key, value in response.items():
                ranges = value['page_range']
                new_range_start = ranges[0] + diff
                new_range_end = ranges[1] + diff
                value['page_range'] = [new_range_start, new_range_end]
        save(pdf, dict_table_contents_dir, response)
        return response

def get_highlights(table_contents, pdf):
    for section, details in table_contents.items():
        if details.get('highlights', None) is not None:
            return extract_text(details['page_range'])

def divide_sections(table_contents):
    dict_sections = {}
    for section, details in table_contents.items():
        text_section = []
        if details.get('highlights', None) is None and details["relevant"]:
            if "subsections" in details:
                for subsubsection, subsubdetails in details["subsections"].items():
                    if subsubdetails["relevant"]:
                        text_section.append(extract_text(subsubdetails['page_range']))
            else:
                text_section.append(extract_text(details['page_range']))
            combined_text = " ".join(filter(None, text_section))
            dict_sections[section] = combined_text
    return dict_sections

def count_tokens(text):
    return len(text) / 4

def join_sections_final(dict_sections, pdf):
    dict_intermediate = {}
    dict_final = {}
    done = []
    combined = {}

    for key, value in dict_sections.items():
        token_count = count_tokens(value)
        if token_count < 24000:
            merged = False
            for key_inter in list(dict_intermediate.keys()):
                if key_inter not in done and count_tokens(dict_intermediate[key_inter]) + token_count < 25000:
                    combined[key_inter] += ', ' + key
                    dict_intermediate[key_inter] += ' ' + value
                    merged = True
                    break
            if not merged:
                dict_intermediate[key] = value
                combined[key] = ''
        else:
            combined[key] = ''
            dict_final[key] = value
            done.extend(list(dict_intermediate.keys()))
    dict_final.update(dict_intermediate)

    save(pdf, pdf_sections_dir, dict_final)
    save(pdf, combinations_dir, combined)
    return dict_final

def call_openai(model, payload, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return model(payload)
        except openai.InternalServerError:
            print(f"Retry {attempt + 1}/{retries} – OpenAI 504 timeout")
            time.sleep(delay)
    raise Exception("Failed after multiple retries")

# === NEW MAIN FUNCTION FOR REUSE ===

def analyze_pdf(pdf_name, override_output_dir=None, ignore_analyzed=False):
    output_dir = override_output_dir or output_dir_default

    with open('analyzed.json', 'r') as f:
        d = json.load(f)

    if not ignore_analyzed and pdf_name in d['Analyzed']:
        print(f"PDF already analyzed: {pdf_name}")
        return None

    print('Analysing PDF: ', pdf_name)

    if is_pdf_long(pdf_name):
        global doc
        doc = fitz.open(f'{folder_path}{pdf_name}')
        print('sending table of contents')
        table_contents = send_table_contents(pdf_name)
        print('dividing sections')
        dict_sections = divide_sections(table_contents)
        print('joining sections')
        dict_final = join_sections_final(dict_sections, pdf_name)
        highlights = get_highlights(table_contents, pdf_name)

        full_dictionary = {}

        print('sending key highlights section:')
        insights = call_openai(key_insights, highlights)
        full_dictionary['risks'] = insights['risks']

        for key, value in dict_final.items():
            print('Sending section:', key)
            risks = call_openai(long_pdfs, value)
            try:
                full_dictionary['risks'].append(risks['risks'])
            except:
                full_dictionary['risks'].append(risks)

        with open(f'{pdf_name}_final_dict', 'w') as f:
            json.dump(full_dictionary, f)

        final = call_openai(join_dicts, str(full_dictionary))
        save(pdf_name, output_dir, final)
        print('done with:', pdf_name)

        d['Analyzed'].append(pdf_name)
        with open('analyzed.json', 'w') as f:
            json.dump(d, f)

        return final

    else:
        print('Sending short pdf in one section')
        result = send_short(pdf_name)
        save(pdf_name, output_dir, result)

        d['Analyzed'].append(pdf_name)
        with open('analyzed.json', 'w') as f:
            json.dump(d, f)

        return result
