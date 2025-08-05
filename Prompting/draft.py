risk_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ExtractedRisks",
    "type": "object",
    "properties": {
    "risks": {
      "type": "object",
      "properties": {
        "risks": {
            "type": "array",
            "title": "ExtractedRisks",
            "items": {
                "type": "object",
                "properties": {
                    "risk_name": {
                        "type": "string",
                        "description": "A short yet descriptive title of the risk. Someone reading just the name should be able to grasp the nature of the risk.",
                        "examples": ["cyber security", "infrastructure", "financial sustainability", "climate change"]
                    },
                    "description": {
                        "type": ["string", "null"],
                        "description": "A concise explanation of what the risk entails, taken from the report. If the text does not provide such information, output null.",
                        "examples": [
                        "Significant price fluctuations in equity markets due to macroeconomic shifts.",
                        "Unauthorized access to customer data via phishing attacks.",
                        null
                        ]
                    },
                    "driver": {
                        "type": ["array", "null"],
                        "description": "List of dictionaries where each dictionary has the driver name as key and driver description as value. Use null if not available in source.",
                        "items": {
                        "type": "object",
                        "description": "Dictionary with driver name as key and description as value. Keys and values are both optional.",
                        "patternProperties": {
                            ".*": {
                            "type": ["string", "null"],
                            "description": "Driver description or null if no description available"
                            }
                        },
                        "additionalProperties": false
                        },
                        "examples": [
                        [
                            {"Interest Rate Hikes": "Regular increases in central bank rates reduce market liquidity"},
                            {"Weak Password Policies": "Simple passwords are easily cracked by automated tools"},
                            {"Economic Uncertainty": null}
                        ],
                        [
                            {"Supply Chain Issues": "Global disruptions affecting material availability"},
                            {"Regulatory Changes": null}
                        ],
                        null
                        ]
                    },
                    "recommendations": {
                        "type": ["array", "null"],
                        "description": "Provide a comprehensive list of recommended actions or treatments to mitigate the risk. If multiple recommendations can be inferred from the text, include all of them rather than limiting the output to one or two. Extract any relevant guidance, such as key questions to consider or highlighted insights that could reasonably be interpreted as recommendations. Use null if not available in source.",
                        "items": {
                        "type": "string",
                        "examples": [
                            "Implement stop-loss orders at 5% intervals.",
                            "Enforce multifactor authentication for all user accounts.",
                            "Establish backup supplier relationships in different geographic regions."
                        ]
                        },
                        "examples": [
                        [
                            "Implement stop-loss orders at 5% intervals.",
                            "Enforce multifactor authentication for all user accounts.",
                            "Establish backup supplier relationships in different geographic regions."
                        ],
                        [
                            "Conduct regular security audits",
                            "Implement incident response procedures"
                        ],
                        None
                        ]
                    },
                    "trend": {
                        "type": ["string", "null"],
                        "description": "Summarize how the risk has evolved over time or is projected to change in the future. If available, include direct statistics or rankings that indicate whether the risk is increasing, decreasing, or remaining stable. This should be as quantifiable as possible. This information may be dispersed across different sections of the document, so ensure all relevant details are consolidated. If no such information is explicitly stated, use null.",
                        "examples": [
                        "Cyber security was ranked as a top risk last year and remains a top risk this year",
                        "Sustainability is becoming significantly more important.",
                        "Increasing year-over-year - ranked #3 last year, now #1",
                        "Stable since 2020 with consistent 15% occurrence rate",
                        "Declining due to improved regulatory frameworks",
                        None
                        ]
                    },
                    "likelihood": {
                        "oneOf": [
                        {
                            "type": "string",
                            "pattern": "^\\d+(\\.\\d+)?%$",
                            "description": "Percentage format like 50%, 12.5%"
                        },
                        {
                            "type": "string",
                            "description": "Descriptive or detailed probability information"
                        },
                        {
                            "type": "null"
                        }
                        ],
                        "description": "Provide information on how likely a risk is to happen. This information will usually be quantifiable, but might not be. Example: information on a risk increasing frequency, or changing nature, or gaining more exposure. If the text does not provide such information, use null.",
                        "examples": [
                            "50%",
                            "12.5%",
                            "85%",
                            "50 percent",
                            "twenty-five percent",
                            "15 percent probability",
                            "High",
                            "15% probability over next 12 months", 
                            "Increasing frequency - up 40% from last year",
                            "Low but rising due to new threat vectors",
                            None
                        ]
                    },
                    "impact": {
                        "type": ["string", "null"],
                        "description": "Provide a detailed description of the potential consequences and severity of the risk. This should include both the nature of the impacts (e.g., financial loss, reputational damage, operational disruption) and the magnitude of the impact if such information is available. If the text indicates changes in severity (e.g., 'Risk X is becoming more severe' or 'Respondents rated this risk higher than last year'), include those details as well. If there are quantifiable scores on impact or importance, include them as well, making sure to include the scale of the score. For example, if the text says 'Risk X was rated 5 out of 10', this should be included in this field. If no such information is explicitly mentioned, use null.",
                        "examples": [
                        "Up to $10M in losses with 6-month recovery period",
                        "Regulatory fines up to $5M plus reputational damage",
                        "Rated 8 out of 10 on severity scale by industry experts",
                        "Operational disruption affecting 70% of customer base",
                        None
                        ]
                    },
                    "risk_indicator": {
                        "type": ["string", "null"],
                        "description": "If the text mentions a specific and quantifiable metric used to assess and track the risk, the response should be the name of a metric. This should be a quantifiable metric such as a certain Ratio, Number of Events/incidents, Frequency of Events, etc. If the indicator is related to the Reports' own research, such as 'Number of respondents who voted this risk as a top risk', this should not be included. If the text does not provide such information, use null.",
                        "examples": [
                            "Value at Risk (VaR)",
                            "Number of critical incidents per quarter",
                            "System uptime percentage",
                            "Credit default ratio",
                            None
                        ]
                    },
                    "risk_events": {
                        "type": ["array", "null"],
                        "description": "Identify and list all specific real-life occurrences related to this risk. Each event should be a concrete, real-world incident mentioned in the text, and should include details. Example: an event that happened in a certain place, in a certain time-period. Avoid generic references (e.g., Cyber Attacks); instead, capture specific instances. If multiple events are provided, include all of them. If no such events are explicitly mentioned, use null.",
                        "items": {
                        "type": "string",
                        "examples": [
                            "March 2024 flash crash - S&P 500 dropped 4% in one day due to algorithmic trading errors",
                            "June 2023 data breach at XYZ Corp exposed 2M customer records via SQL injection",
                            "February 2024 supply chain disruption in Asia affected 15% of global semiconductor production",
                            None
                        ]
                        }
                    },
                    "suggested_audits": {
                        "type": ["array", "null"],
                        "description": "If the text explicitly identifies any audits recommended to evaluate or mitigate the risk—distinct from general recommendations—extract these audit suggestions verbatim and output them as a list. If multiple audit suggestions are provided, include all of them; if none are mentioned, use null. This field should only be populated if the text explicitly refers to an audit.",
                        "items": {
                            "type": "string",
                            "examples": [
                                "IT/OT Compliance Audit",
                                "Access Controls Audit",
                                None
                            ]
                        }
                    },
                    "contextual_variations": {
                        "type": ["array", "null"],
                        "description": "If the text mentions that a certain risk changes in importance, nature, likelihood, impact, etc., according to region, industry, company size, or any other category, extract and include this information here as a list (if there is more than one).",
                        "items": {
                            "type": "string",
                            "examples": [
                                "Fraud is more prominent in tech industry, followed by insurance and education industries",
                                "More severe in emerging markets due to less mature regulatory frameworks",
                                "Highest impact in financial services (8/10) vs. manufacturing (4/10)",
                                "Small companies face 3x higher likelihood due to limited security resources",
                                None
                            ]
                        }
                    } 
                },
                "required": ["risk_name"],
                "additionalProperties": False
            }
        }
    }
}

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
                "Extract and return an array of all distinct risk names "
                "mentioned in the uploaded file. Respond with only the array of strings, "
                "e.g. [\"Cybersecurity Breach\", \"Regulatory Change\", …]."
            )
        }
    ],
    text={ "format": { "type": "text" }},   
    tools=[{
        "type": "file_search",
        "vector_store_ids": [vector_store.id]
    }],
    temperature=0.0
)

# 2️⃣ Parse the JSON array out of the plain-text response
raw = name_resp.output_text.strip()
risk_names = json.loads(raw)  # this turns '["A","B",…]' into a Python list

print(risk_names)

#f"I have these risk names: {risk_names}.For each of these risks, extract the following fields as JSON." + 
response = client.responses.create(
    model="o4-mini-2025-04-16",
    input=[
        {"role": "developer", 
         "content": PROMPT},
        {"role": "user", 
         "content": PROMPT}
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
    reasoning={"effort": "high"}
    #temperature=0.0
    #reasoning_effort='high'
)

#**Extract all risks mentioned in this file with the following fields:**
#Based on the contents of the uploaded file, extract all risks mentioned in this file with the following fields **in details:**