from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load the fine-tuned QA BigBird model
model_name = "google/long-t5-tglobal-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Provide your long context and question
# raw text
with open("chunking/output/output.txt", "r", encoding="utf-8") as f:
    report_text = f.read()
    
prompt = """ 
    You will receive a lengthy text extracted from a PDF report. Your objective is to thoroughly examine the content and identify all key risks mentioned. For each distinct risk, produce a JSON object capturing the following information, directly based on what the text provides:
   1. Risk Name:
   - A short yet descriptive title of the risk. Someone reading just the name should be able to grasp the nature of the risk.
   2. Risk Description:
   - A concise explanation of what the risk entails, taken from the report.  If the text does not provide such information, output N/A.
   3. Risk Driver:
   - A list of dictionaries, where each dictionary represents a specific driver of the risk, containing:
       - Driver Name (subkey)
       - Driver Description (subvalue)
   If the text does not provide such information, output N/A.
   4. Risk Recommendations:
   Provide a comprehensive list of recommended actions or treatments to mitigate the risk. If multiple recommendations can be inferred from the text, include all of them rather than limiting the output to one or two. Extract any relevant guidance, such as key questions to consider or highlighted insights that could reasonably be interpreted as recommendations. If no such information is available, return N/A.
   5. Trend:
   - Summarize how the risk has evolved over time or is projected to change in the future. If available, include direct statistics or rankings that indicate whether the risk is increasing, decreasing, or remaining stable. This should be as quantifiable as possible. For example, this could be statements like "Risk X was ranked as a top risk last year and remains a top risk this year" or "Risk X is becoming significantly more important due to factors X, Y, and Z." This information may be dispersed across different sections of the document, so ensure all relevant details are consolidated. If no such information is explicitly stated, return N/A.
   6. Likelihood:
   - Provide information on how likely a risk is to happen. This information will usually be quantifiable, but might not be. Example: information on a risk increasing frequency, or changing nature, or gaining more exposure. If the text does not provide such information, output N/A.
   7. Impact:
   - Provide a detailed description of the potential consequences and severity of the risk. This should include both the nature of the impacts (e.g., financial loss, reputational damage, operational disruption) and the magnitude of the impact if such information is available. If the text indicates changes in severity (e.g., "Risk X is becoming more severe" or "Respondents rated this risk higher than last year"), include those details as well. If there are quantifiable scores on impact or importance, include them as well, making sure to include the scale of the score. For example, if the text says 'Risk X was rated 5 out of 10', this should be included in this field. If no such information is explicitly mentioned, return N/A.
   8. Risk Indicator:
   - If the text mentions a specific and quantifiable metric used to assess and track the risk, the response should be the name of a metric. This should be a quantifiable metric such as a certain Ratio, Number of Events/incidents, Frequency of Events, etc. If the indicator is related to the Reports' own research, such as 'Number of respondents who voted this risk as a top risk', this should not be included.  If the text does not provide such information, output N/A.
   9. Risk Event:
   - Identify and list all specific real-life occurrences related to this risk. Each event should be a concrete, real-world incident mentioned in the text, and should include details. Example: an event that happened in a certain place, in a certain time-period. Avoid generic references (e.g., "Cyber Attacks"); instead, capture specific instances. If multiple events are provided, include all of them. If no such events are explicitly mentioned, return N/A.
   10. Suggested Audits:
   If the text explicitly identifies any audits recommended to evaluate or mitigate the risk—distinct from general recommendations—extract these audit suggestions verbatim and output them as a list. If multiple audit suggestions are provided, include all of them; if none are mentioned, output "N/A." This field should only be populated if the text explicitly refers to an audit.
   10. Contextual Variations:
   If the text mentions that a certain risk changes in importance, nature, likelihood, impact, etc., according to region, industry, company size, or any other category, extract and include this information here as a list (if there is more than one). Example: 'Risk X is more prominent in X industry, followed by Y and Z industries'.
   Format Requirements:
   - The final output must be a JSON file containing a list of dictionaries.
   - Each dictionary in this list should correspond to one risk.
   - If any required information (e.g., Impact, Trend, Risk Indicator) is not available in the text, use "N/A" for that field.
   Important Notes:
   - All extracted information must come directly from the text. Do not infer, summarize, or generate details that are not explicitly stated. Ensure that every piece of information is accurately captured as presented in the source material, without interpretation or assumption.
   - If the text does not explicitly mention a piece of data, set that field to "N/A".
   - Only list the risks that the text explicitly identifies; do not include extraneous commentary or interpretation.
   - Cover all the important risks mentioned in the entire report.
   - It is likely that the same risk appears multiple times throughout the report, with relevant details—such as its description, drivers, and recommendations—scattered across different sections. To ensure completeness, you should collect and consolidate all details related to the same risk from various parts of the text, ensuring all key aspects are covered.
"""

# Tokenize
input_text = prompt + "\n\n" + report_text

inputs = tokenizer(
    input_text,
    return_tensors="pt",
    max_length=16384,
    truncation=True
)

outputs = model.generate(
    **inputs,
    max_length=2048,  # You can increase if needed
    #num_beams=4,
    do_sample=False,
    early_stopping=True
)

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)

import json

try:
    risks = json.loads(generated_text)
    print(json.dumps(risks, indent=2))
except json.JSONDecodeError:
    print("The model output is not a valid JSON. You may need to clean it manually or add post-processing.")
