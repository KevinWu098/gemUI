import google.generativeai as genai
from dotenv import load_dotenv
import ast
import os

load_dotenv()
GEMINI_API_KEYS=os.environ.get('GEMINI_API_KEYS')

# convert the keys to a JSON list
KEY_LIST = ast.literal_eval(GEMINI_API_KEYS)

# cycle api keys using an index
current_api_key_index = 0

# remember the previous messages
messages = []

def extractUI(prompt, url, html):
    global current_api_key_index
    system_prompt = """
You are a web browser navigation assistant that trims and scrapes relevant portions of the UI for a user.

Whenever a user requests something, you will return a navigator action to switch URLs, or an xpath or id selector to the relevant parts of the UI for a user to look at.

You will only return path or id selectors. If the request requires multiple choices, return ALL RELEVANT selectors that contains the UI that will enable the user to choose the choice themselves.

For example, if there is a container containing two buttons, and it is ambiguous which button the user is interested in, return a selector to the container instead of one of the buttons only.

Output your result in a JSON format in the following:

the type is:
{
  "type": string,
  "selector": string[]
}

{
   "type": either "xpath" or "id",
   "selector": the selector or selectors
}

{
    "type": "navigation",
    "url": url to navigate to
}
"""
    genai.configure(api_key=KEY_LIST[current_api_key_index])
    model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=genai.GenerationConfig(
        max_output_tokens=4000,
        temperature=0,
    ),
    system_instruction=system_prompt)
    
    # grab the previous conversation and add the new prompt
    messages.append({
        'role': 'user',
        'parts': [
prompt + """
Current URL: """ + url + """
HTML: """ + html + """
"""
        ]
    })
    response = model.generate_content(
        messages
    )

    print(response.text)

    # remember the response
    messages.append({
        'role': 'model',
        'parts': [
            response.text
        ]
    })

    # rotate API keys
    current_api_key_index += 1
    if current_api_key_index >= len(KEY_LIST):
        current_api_key_index = 0

    # return the selector object
    return response.text