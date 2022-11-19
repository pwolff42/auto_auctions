# python script to scrape past auctions on carsandbids.com
# Feature list thus far:
# - URL
# - Unique ID (index)
# - year
# - make
# - model
# - mileage
# - VIN
# - Title Status
# - Location
# - Seller
# - Engine
# - Drivetrain
# - Transmission
# - Sell Price (target)
# - bid count
# - reserve status (no reserve or reserve listing)
# - number of views on the page (could be misleading, they count after sale too)
# - auction ending datetime
# - number of photos posted for the listing

# importing packages

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
import seaborn as sns

# pointing to the browser driver
pwolff_path = "/Users/pww/Applications/chromedriver" # Patrick's path
agaba_path = "abhishek's path here" # Abhishek's path
scastillo_path = "Sebastian's path here" # Sebastian's path

# edit the argument of the following to add your driver path before running
s = Service(pwolff_path)

# helper functions:

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

def parse_tag(tags):
    '''
    :param tags: a list of tags with desired information embedded as text
    :return: a list of the text from the tags
    '''
    return [x.text for x in tags]

def url_unique_id(string):
    '''
    :param string: the URL of the page
    :return: the unique identifier of the listing (usually formatted as year-make-model-index)
    '''
    return string.rsplit('/', 1)[-1]

def scrape_listing(listing_soup):
    car_url = listing_soup.find('meta', {'property': 'og:url'}).get('content')
    print(car_url)
    unique_id = url_unique_id(car_url)

    # getting the year of the car from the unique identifier (first 4 characters)
    year = unique_id.split('-')[0]
    # getting the data in the 'quick-facts' table
    quick_facts = listing_soup.find('div', {'class':"quick-facts"})

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
    car = dict(zip(headers, attributes))
    # getting the data from the 'bid-stats' bar
    bid_stats = listing_soup.find('ul', {'class':"bid-stats"})

    # getting the final sell price from the 'bid-stats' bar on the listing page
    bid_value = bid_stats.find('span', {'class':"bid-value"}).text
    # removing formatting with regular expressions
    final_price = re.sub(r'[,$]', '', bid_value)

    # getting the bid count from the 'bid-stats' bar on the listing page
    num_bids = bid_stats.find('li', {'class':"num-bids"}).contents[1] # num-bids has text and then the value at index 1
    bid_count = num_bids.text

    # getting the reserve status of the car (reserve or no reserve)
    # have to circumvent the title attribute of the reserve status element, long attribute containing price in both cases
    reserve_status = listing_soup.find('span', {'title':re.compile('price')}).text

    # getting the number of views on the listing page
    views_xpath = "/html/body/div/div[2]/div[5]/div[1]/div[6]/div/ul/li[3]/div[2]"# pass views icon to check if xpath exists before scraping
    if check_exists_by_xpath(views_xpath) == True:
        try:
            views = listing_soup.find('div', {'class': "td views-icon"}).text
            view_count = re.sub(r',' , '', views) # using regular expressions to remove commas
        except AttributeError:
            view_count = "NA"
    else:
        view_count = "NA"

    # getting the date and time of the auction end from the 'bid-stats' bar on the listing page
    auction_metadata = listing_soup.find('div', {'class':"auction-stats-meta ended"})
    auction_end_datetime = auction_metadata.find('div', {'class': 'td end-icon'}).text
    auction_outcome = auction_metadata.find('div',{'class': 'd-flex bidder'}).text

    # getting the number of photos in the listing
    all_photos_text = listing_soup.find('div', attrs = {'class': 'all', 'data-id': 'all', 'data-section': 'interior'}).text
    # use regular expressions to just get the text in the parentheses
    photo_count = re.findall(r'\((.*?)\)', all_photos_text)[0]
    car['URL'] = car_url
    car['id'] = unique_id
    car['year'] = year
    car['price'] = final_price
    car["auction_outcome"] = auction_outcome # in the case of a sale, "to[insert buyers name]" is also included
    car['bid_count'] = bid_count
    car['reserve_status'] = reserve_status
    car['num_views'] = view_count
    car['end_datetime'] = auction_end_datetime
    car['num_photos'] = photo_count
    return car

# generate a random number between 3  and 5 to use as a delay between requests
def random_delay():
    return random.randint(3,5)

# past auctions link for carsandbids.com
cbauctions = "https://carsandbids.com/past-auctions/"

# opening a browser
browser = webdriver.Chrome(service=s)
browser.get(cbauctions)
time.sleep(1)

carslist = []
bad_urls = []
i = 1

for i in range(1, 202): # 201 pages of listings, not elegant but I know that's how many there are as of 11/19/2022
    print("Scraping page " + str(i))
    browser.get(f"https://carsandbids.com/past-auctions/?page={i}")
    time.sleep(random_delay())
    page_source = browser.page_source
    page_soup = BeautifulSoup(page_source, 'lxml')
    try:
        listing_urls = retrieve_urls(page_soup)
        for url in listing_urls:
            browser.get(f'https://carsandbids.com{url}')
            time.sleep(random_delay())
            listing_source = browser.page_source
            listing_soup = BeautifulSoup(listing_source, 'lxml')
            try:
                car = scrape_listing(listing_soup)
                carslist.append(car)
            except AttributeError:
                print(f"Error with car at https://carsandbids.com{url}")
                bad_urls.append(f'https://carsandbids.com{url}')
                pass
        i += 1
        print("Moving to next page")
    except AttributeError:
        print(f"Error with page {i}")
        pass

browser.close()

# putting scrape results into a dataframe
cars_df = pd.DataFrame(carslist)

# desired save location
directory = 'Enter desired save location here'

# saving the dataframe as a csv to the desired save location
cars_df.to_csv(f'{directory}/cars_df.csv', index=False)

# writing the bad urls to the desired save location
with open(f'{directory}/bad_urls.txt', 'w') as f:
    for url in bad_urls:
        f.write(url + '\n')