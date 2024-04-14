import google.generativeai as genai
import ast
import os
import json
from selenium_functions import extract_elements_by_xpath
import PIL.Image
import re
from constants import *

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
        response = model.generate_content(prompt, request_options={"timeout": 1000})
    else:
        response = model.generate_content(
            [prompt, image], request_options={"timeout": 1000}
        )
    return response.text


def interpret(prompt, url, html, img):
    user_prompt = f"""
    current_url: {url}
    current_page: {html}
    current_screenshot is attached
    Output selectors for relevant elements (divs, inputs, and images) that are relevant to the user's request.x

    user: {prompt}
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
        else:
            dom_elements += f"src: {element['selector']}\n"
    generated_ui = generate_content_with_cycling_keys(
    design_schema
    + "\n\n"
    + dom_elements
    + "\n\n"
    + '"Only output div, button, input, img, and select elements. Do not use Tailwind Classes\nBase Url for images (if any): https://dominos.com \n\n',
    system_prompt_generate,
)
    # remove the ``` and html from the generated_ui response
    generated_ui = generated_ui.replace("```html", "").replace("```", "")
    # fix the special id that has only '' or "" in the special-id
    fixed_generated_ui = fix_special_id(generated_ui)
    return fixed_generated_ui

def fix_special_id(html_string):
    def replace_first_and_last(input_string, char_to_replace, replacement_char):
        print(input_string)
        first_index = input_string.find(char_to_replace)
        last_index = input_string.rfind(char_to_replace)
        print(first_index, last_index)

        if first_index != -1 and last_index != -1:
            if len(input_string) > 0:
                input_string = replacement_char + input_string[1:-1] + replacement_char
                print('replaced:', input_string)
            return input_string
        else:
            return input_string

    def validate(input_str):
        if (input_str.count("\"") == 4):
            print("Too many doubles")
            return replace_first_and_last(input_str, "\"", "\'")
        elif (input_str.count("\'") == 4):
            return replace_first_and_last(input_str, "\'", "\"")
        else:
            return input_str

    after_equals_all = html_string.split("special-id=")[1:] # returns something like "fdasafdsaf other_prop=whatever"
    for id in after_equals_all:
        space_after = None
        space_after = id.split(" ")[0]
        space_after = id.split(">")[0] # returns everything prior to the next right bracket (the end)
        if (" " in space_after):
            space_after = id.split(" ")[0]
        html_string = html_string.replace(space_after, validate(space_after))
    return html_string