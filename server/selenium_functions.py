from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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