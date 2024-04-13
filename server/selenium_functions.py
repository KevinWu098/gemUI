from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def open_browser(browser):
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

def scrape(browser):
    page_html = browser.page_source
     # save the html as a text file
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(page_html)
    return page_html

def scrapeById(browser, id):
    element = browser.find_element(By.ID, id)
    return element

def scrapeByXPath(browser, xpath):
    element = browser.find_element(By.XPATH, xpath)
    return element