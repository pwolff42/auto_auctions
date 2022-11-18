'''
python script to scrape past auctions on carsandbids.com

Feature list thus far:
- URL
- Unique ID (index)
- year
- make
- model
- mileage
- VIN
- Title Status
- Location
- Seller
- Engine
- Drivetrain
- Transmission
- Sell Price (target)
- bid count
- reserve status (no reserve or reserve listing)
- number of views on the page (could be misleading, they count after sale too)
- auction ending datetime
- number of photos posted for the listing



'''
# importing requisite packages

from urllib.request import urlopen
import json
import requests
import time
import re

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import pandas as pd

import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns

# headers for working with the requests library
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"}

# past auctions link for carsandbids.com
# eventually this link will be used in a loop with different paths (subdirectories) to get individual pages
cbauctions = 'https://carsandbids.com/past-auctions/'

# pointing to the browser driver
pwolff_path = "/Users/pww/Applications/chromedriver" # Patrick's path
agaba_path = "abhishek's path here" # Abhishek's path
scastillo_path = "Sebastian's path here" # Sebastian's path

# edit the argument of the following before running
s = Service(pwolff_path) # your driver path goes here

def check_exists_by_xpath(xpath):
    '''
    xpath verification function
    '''
    try:
        browser.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        return False
    return True

def flip_page(next_page_button):
    '''
    :param next_page_button: the xpath of the next page button
    '''
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


def url_unique_id(string):
    '''
    :param string: the URL of the page
    :return: the unique identifier of the listing (usually formatted as year-make-model-index)
    '''
    return string.rsplit('/', 1)[-1]

# getting the URL of the page,
# everything after the last '/' in the url will serve as the unique ID for the car
url_link = page_soup.find('link', {'rel':'canonical'}).get('href')

unique_id = url_unique_id(url_link)

# getting the year of the car from the unique identifier (first 4 characters)
year = unique_id.split('-')[0]

# getting the features from the quick-facts table on each cars and bids listing page
def parse_tag(tags):
    '''
    :param tags: a list of tags with desired information embedded as text
    :return: a list of the text from the tags
    '''
    return [x.text for x in tags]

# getting the data in the 'quick-facts' table
quick_facts = page_soup.find('div', {'class':"quick-facts"})

# features from the quick-facts section are represented in a definition list (dl) html format--a table
# within the dl there are document term (dt) and document description (dd) pairs
# the dts are the features and the dds are the corresponding values
# !important note! if the browser is resized, the order of the definition list changes

# getting the values from the quick-facts table
dd_tags = quick_facts.find_all('dd')
attributes = parse_tag(dd_tags) # all models have 'Save' at the end of the model name

# feature names from the quick-facts table
dt_tags = quick_facts.find_all('dt')
headers = parse_tag(dt_tags)

# making a dictionary of the feature headers and features from the quick facts section
quick_facts_dict = dict(zip(headers, attributes))
quick_facts_dict
# getting the data from the 'bid-stats' bar
bid_stats = page_soup.find('ul', {'class':"bid-stats"})

# getting the final sell price from the 'bid-stats' bar on the listing page
bid_value = bid_stats.find('span', {'class':"bid-value"}).text
# removing formatting with regular expressions
final_price = re.sub(r'[,$]', '', bid_value)

# getting the bid count from the 'bid-stats' bar on the listing page
num_bids = bid_stats.find('li', {'class':"num-bids"}).contents[1] # num-bids has text and then the value at index 1
bid_count = num_bids.text

# getting the reserve status of the car (reserve or no reserve)
# have to circumvent the title attribute of the reserve status element, long attribute containing price in both cases
reserve_status = page_soup.find('span', {'title':re.compile('price')}).text
reserve_status

# getting the number of views on the listing page
views = page_soup.find('div', {'class': "td views-icon"}).text
if views == None:
    view_count = float("nan")
else:
    view_count = re.sub(r',' , '', views) # using regular expressions to remove commas

# getting the date and time of the auction end from the 'bid-stats' bar on the listing page
auction_metadata = page_soup.find('div', {'class':"auction-stats-meta ended"})
auction_end_datetime = auction_metadata.find('div', {'class': 'td end-icon'}).text

# getting the number of photos in the listing
all_photos_text = page_soup.find('div', attrs = {'class': 'all', 'data-id': 'all', 'data-section': 'interior'}).text
# use regular expressions to just get the text in the parentheses
photo_count = re.findall(r'\((.*?)\)', all_photos_text)[0]
photo_count
