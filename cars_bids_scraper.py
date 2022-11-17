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

# function to scrape the reviews from each movie page and appending them to an empty list: all_reviews

def retrieve_listings():
    if check_exists_by_xpath(critic_reviews_xpath):
        element = browser.find_element(By.XPATH,critic_reviews_xpath)
        browser.execute_script("arguments[0].click();", element)
        time.sleep(1)
    else:
        print('No element found!')
    # tomato soupify
    while True:
        page_source = browser.page_source
        tomato_soup = BeautifulSoup(page_source, 'lxml')
        the_reviews = tomato_soup.find_all('div', {'class':re.compile("row review_table_row")})
        for review in the_reviews:
            single_review = ['NA', 'NA']
            rating, text = "NA","NA"
            rating_check = review.find('div', {'class':re.compile("review_icon icon")})
            if rating_check:
                rating = rating_check.get('class')[-1]
                single_review[0] = rating
            text_check = review.find('div', class_ = "the_review").text.strip()
            if len(text_check) > 0:
                text = text_check
                single_review[1] = text
            all_reviews.append(single_review)
        if not check_exists_by_xpath(next_page_button):
            break
        flip_page()
    return all_reviews