# function to scrape a single listing page

def scrape_listing(listing_soup):
    url_link = listing_soup.find('link', {'rel':'canonical'}).get('href')
    unique_id = url_unique_id(url_link)

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
    quick_facts_dict = dict(zip(headers, attributes))
    quick_facts_dict
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
    reserve_status

    # getting the number of views on the listing page
    views = listing_soup.find('div', {'class': "td views-icon"}).text
    if views == None:
        view_count = float("nan")
    else:
        view_count = re.sub(r',' , '', views) # using regular expressions to remove commas

    # getting the date and time of the auction end from the 'bid-stats' bar on the listing page
    auction_metadata = listing_soup.find('div', {'class':"auction-stats-meta ended"})
    auction_end_datetime = auction_metadata.find('div', {'class': 'td end-icon'}).text

    # getting the number of photos in the listing
    all_photos_text = listing_soup.find('div', attrs = {'class': 'all', 'data-id': 'all', 'data-section': 'interior'}).text
    # use regular expressions to just get the text in the parentheses
    photo_count = re.findall(r'\((.*?)\)', all_photos_text)[0]

    car = {
        'URL': url_link,
        'id': unique_id,
        'year': year,
        'make': quick_facts_dict['Make'],
        'model': quick_facts_dict['Model'],
        'mileage': quick_facts_dict['Mileage'],
        'VIN': quick_facts_dict['VIN'],
        'title_status': quick_facts_dict['Title Status'],
        'location': quick_facts_dict['Location'],
        'seller': quick_facts_dict['Seller'],
        'engine': quick_facts_dict['Engine'],
        'drivetrain': quick_facts_dict['Drivetrain'],
        'transmission': quick_facts_dict['Transmission'],
        'sell_price': final_price,
        'bid_count': bid_count,
        'reserve_status': reserve_status,
        'num_views': view_count,
        'end_datetime': auction_end_datetime,
        'num_photos': photo_count
        }
    carslist.append(car)
    return carslist
