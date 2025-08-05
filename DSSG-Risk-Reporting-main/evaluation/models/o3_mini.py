import os
import json
import openai
from dotenv import load_dotenv

# === API KEY ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === PROMPTS ===
prompt_1_for_pdfs =  """ 
    You are a manager in the Enterprise Risk and Assurance Office at UBC (University of British Columbia). Your task is to read large pdfs and understand the key risks and insights from them.
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
    Summarize how the risk has evolved over time or is projected to change in the future. If available, include direct statistics or rankings that indicate whether the risk is increasing, decreasing, or remaining stable. This should be as quantifiable as possible. For example, this could be statements like "Risk X was ranked as a top risk last year and remains a top risk this year" or "Risk X is becoming significantly more important due to factors X, Y, and Z." This information may be dispersed across different sections of the document, so ensure all relevant details are consolidated. If no such information is explicitly stated, return N/A.
    6. Likelihood:
    - Provide information on how likely a risk is to happen. This information will usually be quantifiable, but might not be. Example: information on a risk increasing frequency, or changing nature, or gaining more exposure. If the text does not provide such information, output N/A.
    7. Impact:
   - Provide a detailed description of the potential consequences and severity of the risk. This should include both the nature of the impacts (e.g., financial loss, reputational damage, operational disruption) and the magnitude of the impact if such information is available. If the text indicates changes in severity (e.g., "Risk X is becoming more severe" or "Respondents rated this risk higher than last year"), include those details as well. If there are quantifiable scores on impact or importance, include them as well, making sure to include the scale of the score. For example, if the text says ‘Risk X was rated 5 out of 10’, this should be included in this field. If no such information is explicitly mentioned, return N/A.
    8. Risk Indicator:
    - If the text mentions a specific and quantifiable metric used to assess and track the risk, the response should be the name of a metric. This should be a quantifiable metric such as a certain Ratio, Number of Events/incidents, Frequency of Events, etc. If the indicator is related to the Reports’ own research, such as ‘Number of respondents who voted this risk as a top risk’, this should not be included.  If the text does not provide such information, output N/A. 
    9. Risk Event:
    - Identify and list all specific real-life occurrences related to this risk. Each event should be a concrete, real-world incident mentioned in the text, and should include details. Example: an event that happened in a certain place, in a certain time-period. Avoid generic references (e.g., "Cyber Attacks"); instead, capture specific instances. If multiple events are provided, include all of them. If no such events are explicitly mentioned, return N/A.
    10. Suggested Audits:
    - If the text explicitly identifies any audits recommended to evaluate or mitigate the risk—distinct from general recommendations—extract these audit suggestions verbatim and output them as a list. If multiple audit suggestions are provided, include all of them; if none are mentioned, output "N/A." This field should only be populated if the text explicitly refers to an audit.
    11. Contextual Variations:
    If the text mentions that a certain risk changes in importance, nature, likelihood, impact, etc., according to region, industry, company size, or any other category, extract and include this information here as a list (if there is more than one). Example: ‘Risk X is more prominent in X industry, followed by Y and Z industries’.
    Format Requirements:
    - The final output must be a JSON file containing a list of dictionaries.
    - Each dictionary in this list should correspond to one risk.
    - If any required information (e.g., Impact, Trend, Risk Indicator) is not available in the text, use "N/A" for that field.
    Important Notes:
    - All extracted information must come directly from the text. Do not infer, summarize, or generate details that are not explicitly stated. Ensure that every piece of information is accurately captured as presented in the source material, without interpretation or assumption.
    - If a Risk only has Risk Name and Description and/or Context, remove it from your output, ie do not include it.
    - Only include recommendations that are actionable by companies or similar non-governmental entities. If a recommendation is explicitly targeted at states, governments, or other public sector bodies, do not include it.
    - If the text does not explicitly mention a piece of data, set that field to "N/A".
    - Only list the risks that the text explicitly identifies; do not include extraneous commentary or interpretation.
    - Cover all the important risks mentioned in the entire report. 
    - If the text does not focus on risk, or simply skims over a list of risks, do not output anything. 
    - It is likely that the same risk appears multiple times throughout the report, with relevant details—such as its description, drivers, and recommendations—scattered across different sections. To ensure completeness, you should collect and consolidate all details related to the same risk from various parts of the text, ensuring all key aspects are covered.
    Here is the text:
                """

prompt_2_for_pdfs =  """ 
    You are a manager in the Enterprise Risk and Assurance Office at the University of British Columbia (UBC). Your job is to review long, detailed PDF documents and identify significant risks.
    You will be provided with a portion of extracted text from a report. Carefully examine it and extract all explicitly stated risks. For each, generate a structured JSON object with the following fields:
    1. Risk Name
    - A clear, concise title that reflects the essence of the risk.
    2. Risk Description
    - A summary of what the risk entails, as described in the text. Use "N/A" if not provided.
    3. Risk Drivers
    - A list of driver objects, each containing:
        - Driver Name
        - Driver Description
        - If not available, return "N/A".
    4. Recommendations
    - List all actionable steps suggested to mitigate the risk. Include insights interpreted as recommendations. Use "N/A" if nothing is provided.
    5. Trend Over Time
    - Describe how the risk is changing over time. Include rankings or directional trends. Use "N/A" if unspecified.
    6. Likelihood
    - Report how probable the risk is, based on frequency, exposure, or narrative cues. Use "N/A" if the text is silent on this.
    7. Impact
    - Explain the consequences and potential severity of the risk. Include scores, rankings, or statements of change if available. Use "N/A" if not specified.
    8. Indicators
    - Note any quantifiable metrics used to track the risk (e.g., frequency of incidents). Do not include research-specific survey data. Use "N/A" if none found.
    9. Real-world Risk Events
    - List concrete, dated, or location-specific events associated with the risk. Do not generalize. If not found, return "N/A".
    10. Audit Suggestions
    - Extract explicit audit recommendations, if present. If none are given, return "N/A".
    11. Contextual Differences
    - If the text discusses variations in risk based on factors (industry, region, etc.), list them here. Otherwise, return "N/A".
    Formatting Rules:
    - Output a list of dictionaries in JSON format, each representing one risk.
    - Use "N/A" for fields that are not explicitly addressed in the text.
    - Only include risks with more than a name/description/context.
    - Do not infer or summarize—only extract what is directly in the source.
                """

prompt_3_for_pdfs =  """ 
You are an analyst working in the Enterprise Risk and Assurance Office at the University of British Columbia (UBC). Your responsibility is to review lengthy PDF documents and pinpoint clearly stated significant risks.
You will receive a text excerpt from a report. Review it closely and extract all explicitly mentioned risks. For each identified risk, provide a structured JSON object with the following components:
Risk Name
- A brief and descriptive label summarizing the nature of the risk.
Risk Description
- A concise overview of what the risk entails as described in the passage. If absent, write "N/A".
Risk Drivers
- Include a list of underlying causes or contributing factors. For each, provide:
- Driver Name
- Driver Description
- If either is missing, enter "N/A".
Recommendations
- Extract any proposed actions, guidance, or strategies to mitigate the risk. Interpret implied suggestions when appropriate. Use "N/A" if no recommendations are found.
Trend Over Time
- Indicate any references to whether the risk is growing, diminishing, or stable. Mention any time-based indicators. Use "N/A" if this is not mentioned.
Likelihood
- Describe the chance or probability of the risk occurring, using textual cues or ratings if provided. Write "N/A" if the excerpt does not specify.
Impact
- Detail the potential severity or consequences of the risk. Include quantitative or qualitative references where available. Return "N/A" if missing.
Indicators
- Identify any metrics, data points, or signs used to monitor or track the risk. Do not include academic survey data. Use "N/A" if not present.
Real-world Risk Events
- Note specific incidents or case examples mentioned in the text, including dates or locations if provided. Skip generalizations. If none exist, return "N/A".
Audit Suggestions
- Highlight any auditing steps or reviews recommended for addressing the risk. If no audit guidance is included, respond with "N/A".
Contextual Differences
- If the text compares risk by setting (e.g., geography, sector, or unit), capture those contrasts. Otherwise, return "N/A".
Output Guidelines:
- Format your answer as a JSON array, where each element represents one risk.
- Use "N/A" for any element not clearly mentioned in the source.
- Only include risks with sufficient detail (more than just a name or vague context).
- Do not infer, assume, or summarize beyond what is explicitly written in the text.
                """

prompt_4_for_pdfs =  """ 
You are an analyst in the Enterprise Risk and Assurance Office at the University of British Columbia (UBC). Your role involves analyzing detailed PDF reports to identify and evaluate any explicitly stated significant risks.
Upon receiving an excerpt from a report, carefully examine the content and extract all clearly identified risks. For each risk, generate a structured JSON object that includes the following components:
Risk Name
A brief, descriptive title that summarizes the nature of the risk.
Risk Description
A concise explanation of the risk, as described in the text. If no description is present, write "N/A".
Risk Drivers
A list of contributing factors or causes behind the risk. For each factor, provide:
Driver Name
Driver Description
If either piece of information is missing, write "N/A".
Recommendations
Any suggested actions, strategies, or recommendations aimed at mitigating the risk. If no specific recommendations are offered, enter "N/A".
Trend Over Time
If available, note whether the risk is increasing, decreasing, or stable, including any time-based trends. If no such information is provided, write "N/A".
Likelihood
The probability of the risk occurring. This could be based on textual hints, numerical estimates, or risk ratings. If unspecified, write "N/A".
Impact
An evaluation of the potential consequences or severity of the risk, with quantitative or qualitative details if provided. If no impact is specified, return "N/A".
Indicators
Any metrics, data points, or signals mentioned to monitor or assess the risk. If none are provided, write "N/A".
Real-world Risk Events
Specific incidents or real-world examples of the risk occurring, including dates or locations if mentioned. If there are no specific events, return "N/A".
Audit Suggestions
Any recommendations for audits or reviews that could help address or manage the risk. If there is no audit guidance, enter "N/A".
Contextual Differences
If the risk is compared across different settings (e.g., geographic areas, business units, etc.), capture these comparisons. If no such comparisons exist, write "N/A".
                """

prompt_5_for_pdfs =  """ 
As an analyst working within the Enterprise Risk and Assurance Office at the University of British Columbia (UBC), your task is to carefully review detailed reports and identify any clearly defined risks.
You will receive excerpts from such reports and need to extract any explicitly mentioned risks. For each risk, create a structured JSON object with the following elements:
Risk Name
Provide a clear, concise title summarizing the risk.
Risk Description
Summarize what the risk entails as described in the text. If the description is not provided, write "N/A"
Risk Drivers
Identify the underlying factors contributing to the risk. For each factor, include:
Driver Name
Driver Description
If any part of this is missing, enter "N/A".
Recommendations
List any suggested actions, measures, or strategies intended to address the risk. If there are no recommendations, write "N/A".
Trend Over Time
Note if the risk is changing over time (e.g., increasing, decreasing, or remaining stable). Include time references if available. If no trend is mentioned, write "N/A".
Likelihood
Assess the likelihood of the risk occurring based on the provided information. If the likelihood is not specified, write "N/A".
Impact
Describe the potential consequences or severity of the risk. If no details are given, enter "N/A".
Indicators
Identify any specific metrics or indicators mentioned to track or monitor the risk. If no such data is provided, write "N/A".
Real-world Risk Events
If the text references real-world events related to the risk, include those details (dates, locations, etc.). If no specific events are mentioned, return "N/A".
Audit Suggestions
Mention any audit steps, reviews, or checks suggested to help manage the risk. If no auditing is suggested, use "N/A".
Contextual Differences
If the text compares risks across different contexts (e.g., regions, units, or other relevant settings), summarize those comparisons. If none are made, enter "N/A".
Format:
Provide your answer as a JSON array, where each element corresponds to an identified risk.
If any component is not mentioned in the text, use "N/A".
Only include risks that contain sufficient detail (avoid vague references).
Do not infer any details beyond those explicitly provided in the text.
                """

#ALL_PROMPTS = [prompt_1_for_pdfs, prompt_2_for_pdfs, prompt_3_for_pdfs, prompt_4_for_pdfs, prompt_5_for_pdfs]
ALL_PROMPTS = [prompt_1_for_pdfs, prompt_2_for_pdfs, prompt_3_for_pdfs]
SINGLE_PROMPT = [prompt_1_for_pdfs]

# === FUNCTIONS ===
def _run_risk_analysis(text, prompts):
    outputs = []
    for prompt in prompts:
        full_prompt = prompt + text
        try:
            response = openai.chat.completions.create(
                model='o3-mini',
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": full_prompt}]
                    }
                ],
                response_format={"type": "json_object"},
                reasoning_effort='high',
                timeout=240
            )
            parsed_response = json.loads(response.choices[0].message.content)
            outputs.append(parsed_response)
        except Exception as e:
            print(f"Error with prompt: {e}")
            continue
    return outputs

def risk_analysis_single_prompt(
    input_text,
    override_output_path=None,
    ignore_if_exists=False
):
    if override_output_path and ignore_if_exists and os.path.exists(override_output_path):
        print(f"Skipping: {override_output_path} already exists.")
        return None

    outputs = _run_risk_analysis(input_text, SINGLE_PROMPT)
    result = {"risks": outputs[0]} if outputs else None

    if override_output_path and result:
        os.makedirs(os.path.dirname(override_output_path), exist_ok=True)
        with open(override_output_path, 'w') as f:
            json.dump(result, f, indent=2)

    return result

def risk_analysis_all_prompts(
    input_text,
    override_output_dir=None,
    ignore_if_exists=False
):
    results = []
    os.makedirs(override_output_dir or ".", exist_ok=True)

    for i, prompt in enumerate(ALL_PROMPTS):
        output_path = None
        if override_output_dir:
            output_path = os.path.join(override_output_dir, f"prompt_{i+1}.json")
            if ignore_if_exists and os.path.exists(output_path):
                print(f"Skipping Prompt {i+1}: Output already exists at {output_path}")
                with open(output_path, 'r') as f:
                    results.append(json.load(f))
                continue

        outputs = _run_risk_analysis(input_text, [prompt])
        result = {"risks": outputs[0]} if outputs else None

        if result:
            results.append(result)
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)

    return results