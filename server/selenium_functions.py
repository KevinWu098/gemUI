from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from lxml import html
import re

def open_browser(browser=None):
    if browser:
        browser.quit()
    options = Options()
    options.add_experimental_option("detach", True)

    browser = webdriver.Chrome(options=options)
    browser.get("https://developers.google.com/")
    return browser


def navigate(browser, url):
    browser.get(url)
    return browser


def getUrl(browser):
    return browser.current_url


def scrape(browser):
    # scrape it
    page_html = browser.page_source
    # trim it
    page_html = trimHTML(page_html)
    # save the html as a text file
    with open("output.html", "w", encoding= "utf-8") as f:
        f.write(page_html)
    return page_html


def scrapeById(browser, id):
    # iterate through each id, and get outer html if found
    elements = [browser.find_element(By.ID, i).get_attribute("outerHTML") for i in id]
    return elements


def scrapeByXPath(browser, xpath):
    # iterate through each xpath, and get outer html if found
    xpaths = [
        browser.find_element(By.XPATH, i).get_attribute("outerHTML") for i in xpath
    ]
    return xpaths


def extract_elements_by_xpath(html_string, xpath_selector):
    # Parse the HTML
    tree = html.fromstring(html_string)

    # Apply the XPath selector
    elements = tree.xpath(xpath_selector)

    # Return a list of outer HTML for each element
    return str(
        [html.tostring(element).decode("utf-8") for element in elements]
        + [xpath_selector]
    )


def take_screenshot(browser):
    screenshot = browser.save_screenshot("website.png")


def click(browser, selector):
    try:
        browser.find_element(By.XPATH, selector).click()
    except Exception as e:
        # error in clicking
        print(e)
        print("Error in clicking", selector)


def selenium_type(browser, selector, text):
    browser.find_element(By.XPATH, selector).send_keys(text)


def trimHTML(html_string):
    html_string = remove_non_content_tags(html_string)
    html_string = clear_style_attributes(html_string)
    
    return html_string

def remove_non_content_tags(html_string):
    nonContentTags = [
        "script",
        "style",
        "noscript",
        "br",
        "hr",
        "head",
        "link",
        "meta",
        "title",
        "iframe",
        "audio",
        "svg",
        "img"
    ]

    # Pattern to remove HTML comments
    comments_pattern = r'<!--.*?-->'

    # Remove HTML comments
    html_string = re.sub(comments_pattern, '', html_string, flags=re.DOTALL)

    # Create a regular expression pattern that matches the specified tags
    pattern = r'<({0})\b[^>]*>(.*?)</\1>'.format('|'.join(nonContentTags))

    # Use re.DOTALL to ensure that the dot (.) in the regular expression matches newlines as well
    # Use re.IGNORECASE to make the pattern case insensitive
    # Keep removing tags until there are none left
    while re.search(pattern, html_string, re.DOTALL | re.IGNORECASE):
        html_string = re.sub(pattern, '', html_string, flags=re.DOTALL | re.IGNORECASE)

    # Remove any remaining self-closing non-content tags (e.g., <br/>)
    self_closing_pattern = r'<({0})\b[^>]*/>'.format('|'.join(nonContentTags))
    html_string = re.sub(self_closing_pattern, '', html_string, flags=re.IGNORECASE)

    return html_string

def clear_style_attributes(html_content):
    # Regular expression to match style attributes
    style_pattern = re.compile(r'\s*style\s*=\s*(".*?"|\'.*?\'|[^\'">\s]+)', re.IGNORECASE)
    # Remove style attributes
    return style_pattern.sub('', html_content)