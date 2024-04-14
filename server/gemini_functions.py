import google.generativeai as genai
import ast
import os
import json
from selenium_functions import extract_elements_by_xpath
import PIL.Image

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Convert the GEMINI_API_KEYS string from environment variables to a list
GEMINI_API_KEYS = os.environ.get("GEMINI_API_KEYS")
KEY_LIST = ast.literal_eval(GEMINI_API_KEYS)

# Global index to keep track of the current key
current_api_key_index = 0

# remember the previous messages
messages = []

# all the system prompts
system_prompt_interpret = """
You are a web browser navigation assistant that trims and scrapes relevant portions of the UI for a user.

Whenever a user requests something, you will return an xpath selector, id selector, or src attribute of an image that is relevant to the user.

You will only return path or id selectors. If the request requires multiple choices, return ALL RELEVANT selectors that contains the UI that will enable the user to choose the choice themselves.

For example, if there is a container containing two buttons, and it is ambiguous which button the user is interested in, return a selector to the container instead of one of the buttons only.

If there are images that are relevant to the user, return the src attribute of the image.

Output your result in the following format:

If the user is interested in a specific part of the UI, output your result in the following format:
[
    {
        "type": xpath
        "selector": the selection string
    },
    {
        "type": id
        "selector": the selection string
    },
    {
        "type": src
        "selector": the src attribute of the image
    }
]
"""

system_prompt_generate = """
You are a web browser navigation assistant that generates a user interface for a user to interact with.
You will be given DOM elements from another web browser navigation assistant that trims and scrapes relevant portions of the UI for a user.

Your task is to generate valid HTML strings that can be rendered in a browser, specifically focusing on interactive elements such as buttons and text fields. 
Please use TailwindCSS for styling.

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
        "Use the attached branding guide to style the output. Use the typographies and hex codes defined in the image\n"
        + dom_elements,
        system_prompt_generate,
        image=design,
    )
    # remove the ``` and html from the generated_ui response
    generated_ui = generated_ui.replace("```html", "").replace("```", "")
    return generated_ui
