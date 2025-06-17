
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  
)


prompt = """

    Your task is to extract and structure the Table of Contents from an image of a report's Table of Contents. Your output should be a json dictionary with the following structure:

    {
    "Section Name": {
        "page_range": (start_page, end_page),
        "relevant": true/false
    }
    }

    Instructions:
    1. Extract the Table of Content* from the given image and structure it hierarchically in a JSON dictionary format.
    2. Format the output as follows:
    - Each **section name** is a key in the dictionary.
    - The **value** is a subdictionary containing:
        - `"page_range"`: A tuple `(start_page, end_page)`, representing the page range of that section.
        - `"relevant"`: A boolean value (`true` or `false`) indicating whether the section contains relevant risk information.
    - An optional key "subsections": If a section has subsections, this key should contain a nested subdictionary with the same structure.
    - If the section is ‘Key Highlights’, ‘Key Insights’, ‘Key Takeways’, ‘Key Findings’ or ANYTHING related to this, you should add an optional key called ‘highlights’ and value boolean True.

    Important Note:
    - Verify the actual page numbering by cross-referencing the page numbers from the Table of Contents page with the extracted structure.
    -  To determine the end page of a section, use the start page of the next section and subtract 1 to correctly set the end page for the current section/subsection.  

    Rules for Determining Relevance (`"relevant": true` or `false`):
    - The report is **risk-related**, meaning only sections discussing **risks** should be marked as `"relevant": true`.
    - The following sections, and variations of them **are NOT relevant** (`"relevant": false`):
    - "Methodology"
    - "Appendix"
    - "References"
    - "Endnotes"
    -If there are variations of these sections (variations in name), those should also be ‘false’.


    Additional Considerations:
    - Ensure **accurate extraction** of page numbers and section titles.
    - The **hierarchy of sections should be preserved** (subsections should be nested within their parent section if applicable).
    - **Important:** If the extracted start page of the next section is incorrect or missing, verify its position in the Table of Contents and adjust accordingly. Pay special attention to start and end pages. Always ensure it is accurate.
    - Ensure that **each section's page range does not overlap incorrectly** and that transitions between sections are properly aligned.


    Here is the table of contents as an image:


"""

def table_contents_f(image):
    
    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                            "role": "user",
                            "content": [
                                {
                                "type": "image_url",
                                "image_url": {
                                    "url": f'{image}'
                                }
                                },
                                {
                                "type": "text",
                                "text": f'{prompt}'
                                }
                            ]
                            }
                        ],
                        response_format={
                            "type": "json_object"
                        },
                        temperature=1,
                        max_completion_tokens=2048,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                        )

    parsed_response = json.loads(response.choices[0].message.content)

    return parsed_response