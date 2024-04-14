import google.generativeai as genai
import ast
import os
import json
from selenium_functions import extract_elements_by_xpath
import PIL.Image
import re
from constants import design_schema, system_prompt_generate, system_prompt_interpret

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


def interpret(prompt, url, html_string, img):
    user_prompt = f"""
    Current Page: 
    {html_string}
    
    Current Url:
    {url}
    
    Current_screenshot is attached
    
    Output a plan, then either output selectors, or a navigate object.
    If current page is the requested page, output selectors list.
    user: {prompt}
    """

    # Generate content using the prompt and the website HTML
    response = generate_content_with_cycling_keys(
        user_prompt, system_prompt_interpret, img
    )

    print(response)

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
            "parts": [user_prompt],
        }
    )

    # remember the response
    messages.append({"role": "model", "parts": [response]})

    # return the selector object
    return obj


def generate(html, selectors, url):

    # now generate the new UI

    dom_elements = ""
    for element in selectors:
        if element["type"] == "xpath":
            dom_elements += extract_elements_by_xpath(html, element["selector"])
            dom_elements += "\n"
        else:
            dom_elements += f"src: {element['selector']}\n"
    generated_ui = generate_content_with_cycling_keys(
        design_schema
        + "\n\n"
        + dom_elements
        + "\n\n"
        + f"Only output div, button, input, img, and select elements. Do not use Tailwind Classes\nBase Url for images (if any): {url} \n\n",
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
                print("replaced:", input_string)
            return input_string
        else:
            return input_string

    def validate(input_str):
        if input_str.count('"') == 4:
            print("Too many doubles")
            return replace_first_and_last(input_str, '"', "'")
        elif input_str.count("'") == 4:
            return replace_first_and_last(input_str, "'", '"')
        else:
            return input_str

    after_equals_all = html_string.split("special-id=")[
        1:
    ]  # returns something like "fdasafdsaf other_prop=whatever"
    for id in after_equals_all:
        space_after = None
        space_after = id.split(" ")[0]
        space_after = id.split(">")[
            0
        ]  # returns everything prior to the next right bracket (the end)
        if " " in space_after:
            space_after = id.split(" ")[0]
        html_string = html_string.replace(space_after, validate(space_after))
    return html_string
