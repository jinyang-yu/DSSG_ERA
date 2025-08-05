######### file input
### one-pass: feed the file to the API once
def extract_risks_pass_once(client, file_id, dev_instructions, prompt, model="gpt-4.1-mini-2025-04-14", temperature=0.0):
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "developer",
                "content": dev_instructions
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": file_id
                    },
                    {
                        "type": "input_text",
                        "text": "Based on the contents of the uploaded file, extract all risks mentioned in this file with the following fields **in details:** " + prompt
                    }
                ]
            }
        ],
        temperature=temperature
    )
    return response


### two-pass: feed the file to the API twice
## 1. Count pass
def extract_risks_pass_twice(client, file_id, dev_instructions, prompt, model="gpt-4.1-mini-2025-04-14", temperature=0.0):
    count_resp = client.responses.create(
        model=model,
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
                        "text": """Based on the contents of the uploaded file, how many distinct risks are described? 
                        Respond with only the integer count—no words, no punctuation.""",
                    },
                ]
            }, 
        ],
        temperature=temperature
    )

    raw = count_resp.output_text.strip()
    risk_count = int(raw)  # e.g. 7
    print(f"Found {risk_count} risks.")

    ## 2. Extract pass 
    response = client.responses.create(
        model=model,
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
                        "text": f"""Based on the contents of the uploaded file, 
                        extract {risk_count} risks with the following fields **in details** as JSON.""" +prompt,
                    },
                ]
            },      
        ],
        temperature=temperature
    )
    return response

