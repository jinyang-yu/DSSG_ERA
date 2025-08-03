from openai import OpenAI
import json
from json import JSONDecoder
import requests
from io import BytesIO
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

risk_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ExtractedRisksWrapper",
    "type": "object",
    "properties": {
        "risks": {
            "type": "array",
            "title": "ExtractedRisks",
            "items": {
                "type": "object",
                "description": "A single risk entry with all its required fields.", 
                "properties": {
                    "risk_name": {
                        "type": "string",
                        "description": "A short yet descriptive title of the risk.",
                        "examples": ["cyber security", "infrastructure", "financial sustainability", "climate change", "Insurance"]
                    },
                    "description": {
                        "type": ["string", "null"],
                        "description": "A concise explanation of what the risk entails, taken from the report. Use null if not available in source.",
                        "examples": [
                            "Significant price fluctuations in equity markets due to macroeconomic shifts.",
                            "Unauthorized access to customer data via phishing attacks.",
                            None
                        ]
                    },
                    "driver": {
                        "type": ["array", "null"],
                        "description": "List of drivers, each with a name and (optional) description. Use null if not available in source.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "driver_name": {
                                    "type": "string",
                                    "description": "The name of this individual driver."
                                },
                                "driver_description": {
                                    "type": ["string", "null"],
                                    "description": "Detailed description of the driver, use null if not available in source."
                                }
                            },
                            "required": ["driver_name", "driver_description"],
                            "additionalProperties": False
                        }
                    },
                    "recommendations": {
                        "type": ["array", "null"],
                        "description": "Provide a comprehensive list of recommended actions or treatments to mitigate the risk.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "trend": {
                        "type": ["string", "null"],
                        "description": "Summarize how the risk has evolved over time or is projected to change in the future."
                    },
                    "likelihood": {
                        "type": ["string", "null"],
                        "description": "Provide information on how likely a risk is to happen."
                    },
                    "impact": {
                        "type": ["string", "null"],
                        "description": "Provide a detailed description of the potential consequences and severity of the risk."
                    },
                    "risk_indicator": {
                        "type": ["string", "null"],
                        "description": "If the text mentions a specific and quantifiable metric used to assess and track the risk."
                    },
                    "risk_events": {
                        "type": ["array", "null"],
                        "description": "Identify and list all specific real-life occurrences related to this risk.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "suggested_audits": {
                        "type": ["array", "null"],
                        "description": "If the text explicitly identifies any audits recommended to evaluate or mitigate the risk.",
                        "items": {
                            "type": "string"
                        },
                        "examples": [
                            [
                                "Business Continuity Planning Audit",
                                "Disaster Recovery Audit",
                                "Crisis Management Audit",
                                "Risk Assessment and Management Audit"
                            ],
                            [
                                "Capital Expenditure Audit"
                            ],
                            None
                        ]
                    },
                    "contextual_variations": {
                        "type": ["array", "null"],
                        "description": "If the text mentions that a certain risk changes in importance according to region, industry, etc.",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["risk_name", "description", "driver", "recommendations", "trend", "likelihood", "impact", "risk_indicator", "risk_events", "suggested_audits", "contextual_variations"],
                "additionalProperties": False
            }
        }
    },
    "required": ["risks"],
    "additionalProperties": False
}

#**Extract all risks mentioned in this file with the following fields:**
PROMPT = """
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

client = OpenAI()

# txt_path = 'chunking/raw_text/124raw.txt' chunking/data/124-WEF_The_Global_Risks_Report_2024.pdf
# with open(txt_path, 'r', encoding='utf-8') as f:
#     text = f.read()

prompt_path = 'Prompting/instructions.txt'
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt = f.read()



def create_file(client, file_path):
    if file_path.startswith("http://") or file_path.startswith("https://"):
        # Download the file content from the URL
        response = requests.get(file_path)
        file_content = BytesIO(response.content)
        file_name = file_path.split("/")[-1]
        file_tuple = (file_name, file_content)
        result = client.files.create(
            file=file_tuple,
            purpose="assistants"
        )
    else:
        # Handle local file path
        with open(file_path, "rb") as file_content:
            result = client.files.create(
                file=file_content,
                purpose="assistants"
            )
    print(result.id)
    return result.id

# Replace with your own file path or URL
file_id = create_file(client, 'chunking/raw_text/124raw.txt')

vector_store = client.vector_stores.create(
        name="knowledge_base_124"
)
print(vector_store.id)

result = client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=file_id
)
print(result)

# result1 = client.vector_stores.files.list(
#     vector_store_id=vector_store.id
# )
# print(result1)



# Wait until the vector store status becomes 'completed'
def wait_for_vector_store(vector_store_id, check_interval=5, timeout=300):
    start_time = time.time()

    while True:
        status = client.vector_stores.retrieve(vector_store_id=vector_store_id).status
        print(f"Current status: {status}")
        
        if status == "completed":
            print("Vector store is ready.")
            return True
        elif status == "failed":
            raise RuntimeError("Vector store creation failed.")
        
        if time.time() - start_time > timeout:
            raise TimeoutError("Timeout: Vector store did not complete in time.")
        
        time.sleep(check_interval)

wait_for_vector_store(vector_store.id)

# Define a JSON Schema for an array of risk name strings
risk_name_list_schema = {
    "type": "array",
    "items": { "type": "string" }
}

# count_resp = client.responses.create(
#     model="gpt-4.1-mini-2025-04-14",
#     input=[
#         {"role": "developer", "content": "You are a manager in the Enterprise Risk and Assurance Office."},
#         {"role": "user", 
#          "content": "Based on the contents of the uploaded file, how many distinct risks are described? Respond with only the integer count—no words, no punctuation."}
#     ],
#     text={"format": {"type": "text"}},
#     tools=[{"type": "file_search", "vector_store_ids": [vector_store.id]}],
#     temperature=0.0,
# )



# 3️⃣ Parse the returned count
# raw = count_resp.output_text.strip()
# risk_count = int(raw)  # e.g. 7
# print(f"Found {risk_count} risks.")

name_resp = client.responses.create(
    model="gpt-4.1-mini-2025-04-14",
    input=[
        {
            "role": "developer",
            "content": "You are a manager in the Enterprise Risk and Assurance Office."
        },
        {
            "role": "user",
            "content": (
                "Extract and return a JSON array of all distinct risk names "
                "mentioned in the uploaded file. Respond with only the array of strings, "
                "e.g. [\"Cybersecurity Breach\", \"Regulatory Change\", …]."
            )
        }
    ],
    text={
        "format": {
            "type":   "json_schema",
            "name":   "risk_name_list",
            "schema": risk_name_list_schema,
            "strict": True
        }
    },
    tools=[{
        "type": "file_search",
        "vector_store_ids": [vector_store.id]
    }],
    temperature=0.0
)

risk_names = json.loads(name_resp.output_text)

response = client.responses.create(
    model="gpt-4.1-mini-2025-04-14",
    input=[
        {"role": "developer", 
         "content": prompt},
        {"role": "user", 
         "content": f"I have these risk names: {risk_names}.For each of these risks, extract the following fields as JSON." + PROMPT}
    ],
    text={
        "format": {
            "type":   "json_schema",
            "name":   "risk_extraction",
            "schema": risk_schema,
            "strict": True
        }
    },
    tools=[{
        "type": "file_search",
        "vector_store_ids": [vector_store.id]
    }],
    temperature=0.0
)

data = response.output_text

def parse_prefix_json(text):
    decoder = JSONDecoder()
    obj, idx = decoder.raw_decode(text)
    return obj

result = parse_prefix_json(data)

# 1. Parse the JSON text into Python
# result = json.loads(data)

# 2. Write it to a file
with open("124-fs-c.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Saved results to 124-fs-c.json")