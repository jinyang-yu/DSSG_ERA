
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
        "page_range": (start_page, end_page)
    }
    }

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