'''
python code to scrape past auctions on carsandbids.com

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
cbauctions = 'https://carsandbids.com/past-auctions/'


# pointing to the browser driver
pwolff_path = "/Users/pww/Applications/chromedriver" # Patrick's path
agaba_path = "abhishek's path here" # Abhishek's path
scastillo_path = "Sebastian's path here" # Sebastian's path

# edit the argument of the following before running

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

# getting the data from a single listing page on cars&bids after accessing the link
# test link
example_link = "https://carsandbids.com/auctions/3RZ7NmoN/2021-mercedes-amg-e63-s-wagon"

# opening a browser
browser = webdriver.Chrome(service=s)
browser.get(example_link)
time.sleep(1)


page_source = browser.page_source
page_soup = BeautifulSoup(page_source, 'lxml')
url_link = page_soup.find('link', {'rel':'canonical'}).get('href')
url_link

# last part of the url will serve as the unique ID column for each car, everything after the last '/'
# function to split strings on last / character


# Function to get the last part of the string after the last / character
def url_unique_id(string):
    return string.rsplit('/', 1)[-1]


# testing the function
url_unique_id(url_link)







