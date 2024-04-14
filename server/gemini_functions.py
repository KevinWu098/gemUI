import google.generativeai as genai
import ast
import os
import json
from selenium_functions import extract_elements_by_xpath
import PIL.Image
import re

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Convert the GEMINI_API_KEYS string from environment variables to a list
GEMINI_API_KEYS = os.environ.get("GEMINI_API_KEYS")
KEY_LIST = ast.literal_eval(GEMINI_API_KEYS)

# Randomly shuffle the list of API keys
import random
random.shuffle(KEY_LIST)

# Global index to keep track of the current key
current_api_key_index = 0

# remember the previous messages
messages = []

# all the system prompts
system_prompt_interpret = """
You are a web browser navigation assistant that trims and scrapes relevant portions of the UI for a user. Relevant is defined as the portion of the UI that the user requests for.
Only return selectors or images that are relevant to the user's request.

Whenever a user requests something, you will return the xpath selector or the src attribute of an image that returns the path to the specific file the image is stored in within the client file of the website.
Ensure that all paths end with the file extension of the image (examples are .jpg, .png, .gif, etc.)

If the request requires multiple choices, return ALL RELEVANT selectors that contains the UI that will enable the user to choose the choice themselves.
For example, if there is a container containing two buttons, and it is ambiguous which button the user is interested in, return a selector to the container instead of one of the buttons only.

Output your result in the following format and output as many selectors as necessary. Ensure that the output is a JSON object and that there is a diversity of file paths aligned to the specific types of each image:
[
    {
        "type": xpath
        "selector": selector
    },
    {
        "type": src
        "selector": the src attribute of the image represented as the route to the image inside of the client file of the website
    },
    ...
]
"""

system_prompt_generate = """
You are a web browser navigation assistant that generates a user interface for a user to interact with.
You will be given DOM elements from another web browser navigation assistant that trims and scrapes relevant portions of the UI for a user.

Your task is to generate valid HTML strings that can be rendered in a browser, specifically focusing on interactive elements such as buttons and text fields. 
Please use TailwindCSS for styling. Use actual hex colors for the colors, do not use TailwindCSS classes for colors.

Each element should only have two attributes:
- class: a string of classes separated by spaces, for TailwindCSS styling
- special-id: the XPath or id selector that was given to you, which will be used for identifying the element during interactions
- type: a string that is either 'text', 'button', 'input', or 'img'

Only output images if they are contained in the DOM elements that were given to you.

Output your result in the following format:
<div class='container classes here'>
    <div type='text' class='input classes here'>
        <!-- Additional content here -->
    </div>
    <div type='button' class='button classes here' special-id='button selector here'">
        <!-- Additional content here -->
    </div>
    <input type='input' class='input classes here' special-id='input selector here'>
    <img type='img' class='img classes here' src='image source here'>
</div>
"""

def cycle_api_key():
    global current_api_key_index
    if current_api_key_index >= len(KEY_LIST) - 1:
        current_api_key_index = 0
    else:
        current_api_key_index += 1
    return KEY_LIST[current_api_key_index]


def generate_content_with_cycling_keys(prompt, system_prompt, image=None):
    global current_api_key_index
    # Get the current API key and cycle to the next one for future requests
    api_key = cycle_api_key()

    # Configure the generative AI model with the new API key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-pro-latest",
        generation_config=genai.GenerationConfig(
            max_output_tokens=8000,
            temperature=0,
        ),
        system_instruction=system_prompt,
    )

    # Generate content using the provided prompt
    if image is None:
        response = model.generate_content(prompt)
    else:
        response = model.generate_content([prompt, image])
    return response.text


def interpret(prompt, url, html, img):
    user_prompt = f"""
user: {prompt}

current_url: {url}

current_page: {html}

current_screenshot is attached
"""
    
    # Generate content using the prompt and the website HTML
    response = generate_content_with_cycling_keys(user_prompt, system_prompt_interpret, img)

    if "```json" in response:
        response = response.split("```json")[1].split("```")[0]

    # example: 
    # [{'type': 'xpath',
    #   'selector': '//a[@data-quid="start-your-order-delivery-cta"]'},
    #   {'type': 'xpath',
    #   'selector': '//a[@data-quid="start-your-order-carryout-cta"]'}]
    obj = json.loads(response)

    # grab the previous conversation and add the new prompt
    messages.append(
        {
            "role": "user",
            "parts": [
                user_prompt
            ],
        }
    )

    # remember the response
    messages.append({"role": "model", "parts": [response]})


    # return the selector object
    return obj

def generate(html, selectors):

    # now generate the new UI

    dom_elements = ""
    for element in selectors:
        if element['type'] == 'xpath':
            dom_elements += extract_elements_by_xpath(html, element["selector"])
            dom_elements += "\n"
        elif element['type'] == 'id':
            print("ID selector not handled yet")
            pass
        else:
            dom_elements += f"src: {element['selector']}\n"
    design = PIL.Image.open("design.png")
    generated_ui = generate_content_with_cycling_keys(
    "Use the attached branding guide to style the output. Use the typographies and hex codes defined in the image. Do not use Tailwind Classes\nBase Url for images (if any): https://dominos.com" + dom_elements, system_prompt_generate, image=design
)
    # remove the ``` and html from the generated_ui response
    generated_ui = generated_ui.replace("```html", "").replace("```", "")
    # fix the special id that has only '' or "" in the special-id
    fixed_generated_ui = fix_special_id(generated_ui)
    return fixed_generated_ui

def fix_special_id(html_string):
    def replace_quotes(match):
        special_id_content = match.group(1)
        # Replace single quotes inside the XPath expression with HTML entities
        fixed_content = special_id_content.replace("'", "&apos;")
        # Rebuild the special-id attribute using double quotes
        return f'special-id="{fixed_content}"'
    
    # This regex looks for the special-id attribute and captures its content
    pattern = r'special-id=[\'"]([^\'"]+)[\'"]'
    # Use the sub function to replace the matched special-id attributes
    fixed_html = re.sub(pattern, replace_quotes, html_string)
    
    return fixed_html