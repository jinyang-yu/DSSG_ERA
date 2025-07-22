response = client.responses.create(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "You are a risk analyst. You will be given a risk report and should extract the relevant information and convert it into a structured format."},
        {"role": "user", "content": "what is the risk name?"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "math_response",
            "schema": {
                "type": "object",
                "properties": {
                    "risk name": { "type": "string" },
                    "risk description": { "type": "string" },
                    "risk driver name": { "type": "string" },
                    "risk driver description": { "type": "string" },
                    "risk trend": { "type": "string" },
                    "likelihood": { "type": "number" },
                    "impact": { "type": "string" },
                    "risk indicator": { "type": "string" },
                    "risk event": { "type": "string" },
                    "risk recommendation": { "type": "string" },
                    "suggested audits": { "type": "string" },
                    "contextual variation": { "type": "string" },
                },
                "required": ["risk name"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

print(response.output_text)