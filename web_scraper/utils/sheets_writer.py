# utils/sheets_writer.py 

import gspread
from google.oauth2.service_account import Credentials
from typing import List

scopes = [
  "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("data/credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1L7xnQGCdX7L8Hczp1uqtrr8FMfyk5Yyf3ud2LZ2MfsA"
sheet = client.open_by_key(sheet_id)

def write_to_tab(date: str, pdf_list: List[str]):
  """
  Write PDF list if exists to new tab in Google Sheets 

  Args:
    date (datetime): Date that analysis run - used for tab name
    pdf_list (List): List of links to inspect
  """
  reshaped_list = [[pdf] for pdf in pdf_list]

  try: 
    worksheet = sheet.add_worksheet(title=date, rows="100", cols="20")
    worksheet.update("A1", reshaped_list)
  except gspread.exceptions.APIError:
    worksheet = sheet.worksheet(date)
    worksheet.clear()
    worksheet.update("A1", reshaped_list)



