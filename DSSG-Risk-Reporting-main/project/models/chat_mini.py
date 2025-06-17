from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  
)

prompt =  """ 
    You will receive the ‘Key Insights’ section of a risk report extracted from a PDF report. Your objective is to thoroughly examine the content and identify the key risks mentioned. For each distinct risk, produce a JSON object capturing the following information, directly based on what the text provides:
    1. Risk Name:
    - A short yet descriptive title of the risk. Someone reading just the name should be able to grasp the nature of the risk.
    2. Risk Driver:
    - A list of dictionaries, where each dictionary represents a specific driver of the risk, containing:
        - Driver Name (subkey) 
        - Driver Description (subvalue)
    If the text does not provide such information, output N/A.
    3. Risk Recommendations:
    If the text mentions how companies should mitigate that risk, provide a comprehensive list of recommended actions or treatments to mitigate the risk. If multiple recommendations can be inferred from the text, include all of them rather than limiting the output to one or two.  If no such information is available, return N/A.
    4. Trend:
    Summarize how the risk has evolved over time or is projected to change in the future. If available, include direct statistics or rankings that indicate whether the risk is increasing, decreasing, or remaining stable. This should be as quantifiable as possible. For example, this could be statements like "Risk X was ranked as a top risk last year and remains a top risk this year" or "Risk X is becoming significantly more important due to factors X, Y, and Z." This information may be dispersed across different sections of the document, so ensure all relevant details are consolidated. If no such information is explicitly stated, return N/A.
    5. Likelihood:
    - Provide information on how likely a risk is to happen. This information will usually be quantifiable, but might not be. Example: information on a risk increasing frequency, or changing nature, or gaining more exposure. If the text does not provide such information, output N/A.
    6. Impact:
    Provide a detailed description of the potential consequences and severity of the risk. This should include both the nature of the impacts (e.g., financial loss, reputational damage, operational disruption) and the magnitude of the impact if such information is available. If the text indicates changes in severity (e.g., "Risk X is becoming more severe" or "Respondents rated this risk higher than last year"), include those details as well. If there are quantifiable scores on impact or importance, include them as well, making sure to include the scale of the score. If no such information is explicitly mentioned, return N/A.
    7. Risk Indicator:
    - If the text mentions a specific and quantifiable metric used to assess and track the risk. Te response should be the name of a metric. This should be a quantifiable metric such as a certain Ratio, Number of Events/incidents, Frequency of Events, etc.  If the text does not provide such information, output N/A.
    8. Risk Event:
    - Identify and list all specific real-life occurrences related to this risk. Each event should be a concrete, real-world incident mentioned in the text, and should include details. Example: an event that happened in a certain place, in a certain time-period. Avoid generic references (e.g., "Cyber Attacks"); instead, capture specific instances. If multiple events are provided, include all of them. If no such events are explicitly mentioned, return N/A.
    9. Contextual Variations:
    If the text mentions that a certain risk changes in importance, nature, likelihood, impact, etc., according to region, industry, company size, or any other category, extract and include this information here as a list (if there is more than one). Example: ‘Risk X is more prominent in X industry, followed by Y and Z industries’.
    Format Requirements:
    - The final output must be a JSON file containing a list of dictionaries.
    - Each dictionary in this list should correspond to one risk.
    - If any required information (e.g., Impact, Trend, Risk Indicator) is not available in the text, use "N/A" for that field.
    Important Notes:
    - All extracted information must come directly from the text. Do not infer, summarize, or generate details that are not explicitly stated. Ensure that every piece of information is accurately captured as presented in the source material, without interpretation or assumption.
    - If the text does not explicitly mention a piece of data, set that field to "N/A".
    - Only list the risks that the text explicitly identifies; do not include extraneous commentary or interpretation.
    - If the text does not focus on risk, or simply skims over a list of risks, do not output anything. 
    Here is the text:

                """


def key_insights(text):
    print('Sending Key Insights Section')
    input = str(prompt + text)
    system_input = 'You are a manager in the Enterprise Risk and Assurance Office at UBC. Your task is to read large pdfs and understand the key risks and insights from them.'
    response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": system_input
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": input
            }
        ]
        }
    ],
    response_format={
        "type": 'json_object'
    },
    temperature  = 0.5,
    max_completion_tokens=15000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    
    )
    
    parsed_response = json.loads(response.choices[0].message.content) 

    return parsed_response