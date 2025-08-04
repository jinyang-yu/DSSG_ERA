# 4o_mini_processor.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def classify_risk(text: str) -> str:
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

  prompt = f"""
    You will receive a long string of parsed HTML content from a web-scraped news article. The text will include a mix of meaningful article content and irrelevant sections such as navigation menus, footers, accessibility notices, subscription blurbs, and copyright disclaimers.

    Please analyze **only the main body of the article** — the actual news story describing real-world events or developments. Ignore all headers, menus, accessibility text, promotional or subscription material, and website footers. The example content that you will receive will only contain a shortened version of the article just for you to learn the context.

    Your task is to determine whether the article is **relevant to risks** that may affect:
    - The University of British Columbia (UBC)
    - International students
    - Post-graduate students
    - Post-secondary institutions
    - Education
    - Canada or North America in general

    Relevance means the article describes risks that are:
    - Systemic or institutional in nature
    - Related to higher education, research, public institutions, international relations, technology, regulation, or public health
    - Potentially impactful to UBC, international students, post-secondary education, or the broader academic/governmental ecosystem
    Exclude:
    - Isolated incidents of crime (e.g., stabbings, hijackings, local arrests)
    - General-interest news, sports, entertainment, or celebrity culture
    - Any story not tied to trends, policy changes, infrastructure, regulation, or sectoral risk

    Return:
    - 'True' if the article is relevant to risks for UBC's Enterprise Risk and Assurance (ERA) team to note
    - 'False' if the article is about general interest, sports, entertainment, or is otherwise unrelated

    Example 1:
    Input: "Philadelphia Eagles linebacker Nakobe Dean is carted off the field after an injury during the first half of an NFL wild-card playoff football game against the Green Bay Packers on Jan. 12, 2025, in Philadelphia. (AP Photo/Derik Hamilton)

    Some of the most important players on NFL teams are those that might not necessarily start the season on the field.

    Depth is crucial during a rigorous 17-game regular-season schedule that’s preceded by a month of training camp practices in hot conditions as players try to make team’s 53-man active rosters.

    Injuries can play as big a role in an NFL team’s successes or failures as the best game plans. 

    ..."
    Answer: False

    Example 2:
    Input: "The findings show international students increasingly turning away from the US, Canada and Australia, and could signal an end to the decades-long dominance of the ‘big four’ trading market share, the report by Studyportals, NAFSA and Oxford Test of English suggests.

    “For the first time, we’re seeing the big four’s collective market share shrink, and that market share being captured by non-big four destinations,” said Studyportals head of communication, Cara Skikne.

    The research offers near real-time data on student enrolment for the January – March 2025 intake, from 240 institutions across 48 countries.

    ...

    “The impact of restrictive government policies is far from over; we expect them to continue casting a long shadow over international enrolments,” said Skikne.

    “At the same time, institutions are being pushed to achieve more with fewer resources, juggling ambitious enrolment targets amid tightening budgets and shrinking teams,” she added.

    After diversification, institutions highlighted expanding online programs, the increased use of AI and large changes to programs and subjects – particularly in the UK and Canada – identified as expected trends for the coming year."
    Answer: True

    Example 3:
    Input: "Tweet
    Medical students in South Korea have said they will return to their university courses after an extended boycott that lasted almost a year and a half. However, student groups have not specified when or how the return would take place, while medical schools face considerable hurdles organising the education of different cohorts after so many months of disruption.

    The Korean Medical Students Association (KMSA) issued a joint statement alongside the Korean Medical Association (KMA) and the chairs of the Education and Health and Welfare Committees of the National Assembly during a press conference at KMA headquarters in Yongsan, Seoul, on 12 July... The joint declaration demanded guaranteed participation from medical students in future discussions concerning medium- and long-term improvements to the education and training environment.

    Receive email updates from UWN Global newsletters Africa newsletters Other (other includes related events and webinars)
    Data will be processed according to our standard terms & conditions.
    Sponsored Article"
    Answer: False

    Input: "{text}"
    Answer:
    """

  
  try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_input},
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
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
