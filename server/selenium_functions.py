from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from lxml import html

def open_browser(browser=None):
    if (browser):
        browser.quit()
    options = Options()
    options.add_experimental_option("detach", True)

    browser = webdriver.Chrome(options=options)
    browser.get('https://developer.chrome.com/')
    return browser

def navigate(browser, url):
    browser.get(url)
    return browser

def getUrl(browser):
    return browser.current_url

def scrape(browser):
    # trim it
    trimHTML(browser)
    # scrape it
    page_html = browser.page_source
     # save the html as a text file
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(page_html)
    return page_html

def scrapeById(browser, id):
    # iterate through each id, and get outer html if found
    elements = [browser.find_element(By.ID, i).get_attribute('outerHTML') for i in id]
    return elements

def scrapeByXPath(browser, xpath):
    # iterate through each xpath, and get outer html if found
    xpaths = [browser.find_element(By.XPATH, i).get_attribute('outerHTML') for i in xpath]
    return xpaths

def extract_elements_by_xpath(html_string, xpath_selector):
    # Parse the HTML
    tree = html.fromstring(html_string)

    # Apply the XPath selector
    elements = tree.xpath(xpath_selector)

    # Return a list of outer HTML for each element
    return str([html.tostring(element).decode("utf-8") for element in elements] + [xpath_selector])

def take_screenshot(browser):
    screenshot = browser.save_screenshot("website.png")

def click(browser, selector):
    browser.find_element(By.XPATH, selector).click()

def selenium_type(browser, selector, text):
    browser.find_element(By.XPATH, selector).send_keys(text)

def trimHTML(browser):
    nonContentTags = [
            "SCRIPT",
            "STYLE",
            "NOSCRIPT",
            "BR",
            "HR",
            "HEAD",
            "LINK",
            "META",
            "TITLE",
        ]
    for tag in nonContentTags:
        browser.execute_script("""
        var elements = document.getElementsByTagName('""" + tag + """);
        while (elements.length > 0) {
            elements[0].parentNode.removeChild(elements[0]);
        }
    """)