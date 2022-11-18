# function to get the soup of a listing page so that it can be passed to scrape_listing()
page_source = browser.page_source # see what is returned by this, if it is a link, great

def soupify_listing(page_source):
    listing_soup = BeautifulSoup(page_source, 'lxml')
    return listing_soup