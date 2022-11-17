'''
Creating a scraper for Cars and Bids
'''

# importing requisite packages

import requests
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd

# homepage link for carsandbids.com
cbhome = "https://carsandbids.com/"

# pointing to the browser driver

pwolff_path = "/Users/pww/Applications/chromedriver"
# agaba_path =
# scastillo_path =

s = Service(pwolff_path) # your driver path goes here

# xpath verification function

def check_exists_by_xpath(xpath):
    try:
        browser.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        return False
    return True

# page turner function with 1 second time sleep

def flip_page(next_page_button):
    next_page_exists = check_exists_by_xpath(next_page_button)
    if next_page_exists:
        element = browser.find_element(By.XPATH, next_page_button)
        browser.execute_script("arguments[0].click();", element)
        time.sleep(1)
    else:
        print("no more pages!")

