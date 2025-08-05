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