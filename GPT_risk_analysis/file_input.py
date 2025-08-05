from openai import OpenAI
import json
from json import JSONDecoder
import requests
from io import BytesIO
import os
from dotenv import load_dotenv
import time
import upload_file

### Load environment variables from .env file
load_dotenv()

### creates an instance of the OpenAI client
client = OpenAI()

### importing developer instructions
prompt_path = 'Prompting/instructions.txt'
with open(prompt_path, 'r', encoding='utf-8') as f:
    dev_instructions = f.read()

### user message
PROMPT = """ For each of the following fields, please provide information as **detailed** as you can:
1. Risk Name:
- A short yet descriptive title of the risk. Someone reading just the name should be able to grasp the nature of the risk.
2. Risk Description:
- A concise explanation of what the risk entails, taken from the report.  If the text does not provide such information, output null.
3. Risk Driver:
- A list of dictionaries, where each dictionary represents a specific driver of the risk, containing:
    - Driver Name
    - Driver Description
    If the text does not provide such information, output null.
4. Risk Recommendations:
- Provide a comprehensive list of recommended actions or treatments to mitigate the risk. If multiple recommendations can be inferred from the text, include all of them rather than limiting the output to one or two. Extract any relevant guidance, such as key questions to consider or highlighted insights that could reasonably be interpreted as recommendations. If no such information is available, output null.
5. Trend:
- Summarize how the risk has evolved over time or is projected to change in the future. If available, include direct statistics or rankings that indicate whether the risk is increasing, decreasing, or remaining stable. This should be as quantifiable as possible. For example, this could be statements like "Risk X was ranked as a top risk last year and remains a top risk this year" or "Risk X is becoming significantly more important due to factors X, Y, and Z." This information may be dispersed across different sections of the document, so ensure all relevant details are consolidated. If no such information is explicitly stated, output null.
6. Likelihood:
- Provide information on how likely a risk is to happen. This information will usually be quantifiable, but might not be. Example: information on a risk increasing frequency, or changing nature, or gaining more exposure. If the text does not provide such information, output null.
7. Impact:
- Provide a detailed description of the potential consequences and severity of the risk. This should include both the nature of the impacts (e.g., financial loss, reputational damage, operational disruption) and the magnitude of the impact if such information is available. If the text indicates changes in severity (e.g., "Risk X is becoming more severe" or "Respondents rated this risk higher than last year"), include those details as well. If there are quantifiable scores on impact or importance, include them as well, making sure to include the scale of the score. For example, if the text says 'Risk X was rated 5 out of 10', this should be included in this field. If no such information is explicitly mentioned, output null.
8. Risk Indicator:
- If the text mentions a specific and quantifiable metric used to assess and track the risk, the response should be the name of a metric. This should be a quantifiable metric such as a certain Ratio, Number of Events/incidents, Frequency of Events, etc. If the indicator is related to the Reports' own research, such as 'Number of respondents who voted this risk as a top risk', this should not be included.  If the text does not provide such information, output null. 
9. Risk Event:
- Identify and list all specific real-life occurrences related to this risk. Each event should be a concrete, real-world incident mentioned in the text, and should include details. Example: an event that happened in a certain place, in a certain time-period. Avoid generic references (e.g., "Cyber Attacks"); instead, capture specific instances. If multiple events are provided, include all of them. If no such events are explicitly mentioned, output null.
10. Suggested Audits:
- If the text explicitly identifies any audits recommended to evaluate or mitigate the risk—distinct from general recommendations—extract these audit suggestions verbatim and output them as a list. If multiple audit suggestions are provided, include all of them; if none are mentioned, output null. This field should only be populated if the text explicitly refers to an audit.
11. Contextual Variations:
If the text mentions that a certain risk changes in importance, nature, likelihood, impact, etc., according to region, industry, company size, or any other category, extract and include this information here as a list (if there is more than one). Example: 'Risk X is more prominent in X industry, followed by Y and Z industries'."""




### Upload the file to the File API
file_id = upload_file.create_file(client, 'chunking/data/15-higher-education-sector-risk-profile-2023.pdf')
# or url: e.g. "https://cdn.openai.com/API/docs/deep_research_blog.pdf"
print(file_id)


######### file input
### one-pass: feed the file to the API once
# response = client.responses.create(
#     model="gpt-4.1-mini-2025-04-14",
#     input=[
#         {"role": "developer", 
#          "content": dev_instructions},
#         {"role": "user", 
#          "content": [
#                 {
#                     "type": "input_file",
#                     "file_id": file_id,
#                 },
#                 {
#                     "type": "input_text",
#                     "text": "Based on the contents of the uploaded file, extract all risks mentioned in this file with the following fields **in details:**" + PROMPT,
#                 },
#             ]
#         },      
#     ],
#     temperature=0.0
# )

### two-pass: feed the file to the API twice
## 1. Count pass
count_resp = client.responses.create(
    model="gpt-4.1-mini-2025-04-14",
    input=[
        {"role": "developer", "content": "You are a manager in the Enterprise Risk and Assurance Office."},
        {"role": "user", 
         "content": [
                {
                    "type": "input_file",
                    "file_id": file_id,
                },
                {
                    "type": "input_text",
                    "text": "Based on the contents of the uploaded file, how many distinct risks are described? Respond with only the integer count—no words, no punctuation.",
                },
            ]
        }, 
    ],
    temperature=0.0
)

raw = count_resp.output_text.strip()
risk_count = int(raw)  # e.g. 7
print(f"Found {risk_count} risks.")

## 2. Extract pass 
response = client.responses.create(
    model="gpt-4.1-mini-2025-04-14",
    input=[
        {"role": "developer", 
         "content": dev_instructions},
        {"role": "user", 
         "content": [
                {
                    "type": "input_file",
                    "file_id": file_id,
                },
                {
                    "type": "input_text",
                    "text": f"Based on the contents of the uploaded file, extract {risk_count} risks with the following fields **in details** as JSON." +PROMPT,
                },
            ]
        },      
    ],
    temperature=0.0
)

data = response.output_text

def parse_prefix_json(text):
    decoder = JSONDecoder()
    obj, idx = decoder.raw_decode(text)
    return obj

## 1. Parse the JSON text into Python
result = parse_prefix_json(data)
# result = json.loads(data)

## 2. Write it to a file
with open("162-file-search-2-txt.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Saved results to 162-file-search-2-txt.json")