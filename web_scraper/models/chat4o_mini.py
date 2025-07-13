# 4o_mini_processor.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def check_relevancy(text: str) -> str:
  """
  Given the parsed HTML output from web-scraped content, check if the main article body is relevant to risks
  that could affect the nature of ERA's work and UBC.

  Args:
      text (str): Cleaned content of web-page scraped through BeautifulSoup

  Returns:
      str: 'True' if relevant, 'False' otherwise
  """

  system_input = (
      "You are manager in the Enterprise Risk and Assurance (ERA) Office at UBC, analyzing large volumes "
      "of publicly available textual data - such as news articles, research papers and industry reports - to identify and assess "
      "risks that may affect the University of British Columbia (UBC), its international and post-graduate students, "
      "the post-secondary sector, and Canada/North America more broadly."
  )

  prompt = (
      "You will receive a long string of parsed HTML content from a web-scraped news article. "
      "The text will include a mix of meaningful article content and irrelevant sections such as navigation menus, footers, accessibility notices, subscription blurbs, and copyright disclaimers.\n\n"
      "Please analyze **only the main body of the article** — the actual news story describing real-world events or developments. "
      "Ignore all headers, menus, accessibility text, promotional or subscription material, and website footers.\n\n"
      
      "Your task is to determine whether the article is **relevant to risks** that may affect:\n"
      "- The University of British Columbia (UBC)\n"
      "- International students\n"
      "- Post-graduate students\n"
      "- Post-secondary institutions\n"
      "- Canada or North America in general\n\n"

      "Relevance means the article discusses significant developments, threats, trends, or issues that could impact education, research, safety, geopolitics, the economy, technology, regulation, public health, or other societal risks relevant to these entities.\n\n"

      "Return:\n"
      "- 'True' if the article is relevant to risks for UBC's Enterprise Risk and Assurance (ERA) team to note\n"
      "- 'False' if the article is about general interest, sports, entertainment, or is otherwise unrelated\n\n"

      "Example 1:\n"
      "Input: 'Florida Panthers just a win away from 2nd consecutive Stanley Cup | CBC News\\nContent\\nSkip to Main ContentAccessibility Help\\nMenu\\nWhen search suggestions are available ... \\nThe Panthers beat out the Oilers to win the Stanley Cup in Game 7 ... \\nSince opening night of their title defence, the Panthers have won 32 of 50 games at their arena ... \\nCBC's Journalistic Standards and Practices·About CBC NewsCorrections and clarifications·Submit a news tip·Report error\\n...'\n"
      "Answer: False\n\n"

      "Example 2:\n"
      "Input: 'Israel-Iran conflict: 80,000 Canadians are in the Middle East\\nSkip to main content\\nSectionsLocalWildfiresShopping TrendsOpens in new windowCTV News AppWatchCTV News NowIn Pictures\\nSign In\\nCTV News App\\nAtlantic\\nNova Scotia\\nNew Brunswick\\nPrince Edward Island\\nNewfoundland and Labrador\\n...\\nAround 80,000 Canadians in the Middle East amid Israel-Iran conflict: Global Affairs\\nBy The Canadian Press\\nPublished: June 17, 2025 at 11:14AM EDT\\nWith global tensions rising, CTV’s Colton Praill previews key issues set to dominate the G7 Summit in Alberta, including the crisis in the Middle East.\\nVideo\\nGardiner Expressway reopens after carjacking suspect injured while fleeing from officers on highway\\nCanada-wide warrant issued for suspect in deadly assault of international student: Peel police\\n...\\nCTV National News\\nCaptured on Camera\\nPolitics\\nLifestyle\\nConsumer\\nHealth\\nEntertainment\\nTechnology\\nAutos\\nEnvironment\\nLive\\nIn Pictures\\n...\\nADVERTISEMENT'\n"
      "Answer: True"

      f"Input: '{text}'\nAnswer:"
    )
  
  try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_input},
            {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=20,
            )

    output = response.choices[0].message.content.strip()

    if isinstance(output, str):
      if output.lower() == "true":
          return "True"
      elif output.lower() == "false":
          return "False"
      else:
          raise ValueError(f"Unexpected model output: {output!r}")
    else:
      raise TypeError(f"Expected string response, got: {type(output)}")

  except Exception as e:
      print(f"[Error] Failed to evaluate relevancy: {e}")
      return "Error"
