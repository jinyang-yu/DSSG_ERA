from openai import OpenAI
import json
from json import JSONDecoder
from dotenv import load_dotenv
import os

import upload_file
import file_input
import file_search


# Load environment variables from .env file
load_dotenv()

### creates an instance of the OpenAI client
client = OpenAI()

### importing developer instructions
instructions_path = 'risk_analysis/instructions.txt'
with open(instructions_path, 'r', encoding='utf-8') as f:
    dev_instructions = f.read()

### User message
prompt = """ For each of the following fields, please provide information as **detailed** as you can:
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


def pdfs_risk_analysis(client, folder_path, record_file="processed_files.txt", method="file_search", pass_type = 1):
    # Step 1: Load previously processed filenames into a set
    if os.path.exists(record_file):
        with open(record_file, "r") as f:
            processed = set(line.strip() for line in f)
    else:
        processed = set()

    # Step 2: Loop through all PDF files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf") and filename not in processed:
            full_path = os.path.join(folder_path, filename)
            file_id = upload_file.create_file(client, full_path)
            print(f"Uploaded: {filename}")

            # Step 3: Record this file as processed
            with open(record_file, "a") as f:
                f.write(filename + "\n")

            # Step 4: Extract risks based on method and pass_type
            if method == "file_input":
                if pass_type == 1:
                    response = file_input.extract_risks_pass_once(client, file_id, dev_instructions, prompt)
                elif pass_type == 2:
                    response = file_input.extract_risks_pass_twice(client, file_id, dev_instructions, prompt)
                else:
                    raise ValueError("Invalid pass_type. Use 'one' or 'two'.")
            elif method == "file_search":
                vec_id = file_search.vectorization(client, "knowledge_base", file_id)
                if pass_type == 1:
                    response = file_search.extract_risks_pass_once(client, file_id, vec_id, dev_instructions, prompt)
                elif pass_type == 2:
                    response = file_search.extract_risks_pass_twice(client, file_id, vec_id, dev_instructions, prompt)
                else:
                    raise ValueError("Invalid pass_type. Use 'one' or 'two'.")
            else:
                raise ValueError("Invalid method. Use 'file_input' or 'file_search'.")

            # Step 5: Handle output
            data = response.output_text

            def parse_prefix_json(text):
                decoder = JSONDecoder()
                obj, idx = decoder.raw_decode(text)
                return obj

            result = parse_prefix_json(data)

            # Clean the PDF filename (remove extension and unsafe characters)
            base_name = os.path.splitext(filename)[0]
            safe_base_name = base_name.replace(" ", "_")  # Optional: make it safer for filenames

            # Generate output filename
            output_filename = f"{safe_base_name}_{method}_{str(pass_type)}.json"

            # Save the result
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Saved results to {output_filename}")



