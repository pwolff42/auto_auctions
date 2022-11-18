# function to navigate over a list of scraped urls on carsandbids

def retreive_urls():
    listing_grid = page_soup.find('ul', {'class': 'auctions-list past-auctions'})
    auction_items = listing_grid.find_all('li', {'class': 'auction-item'})
    listing_a_tags = set(listing_grid.find_all('a', {'href': re.compile('/auctions/')})['href'])
