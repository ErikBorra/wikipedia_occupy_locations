import scraperwiki # used for running the scraper and storing data
import requests # used for retrieving data
from bs4 import BeautifulSoup # used for parsing data
import re # used for regular expressions

# store results in structured format
def add_location(continent, country, city, db):
    db.append({
        'continent': continent,
        'country': country,
        'city': city
    })

# parse table for locations
def scan_table(table, continent, db):
    rows = table.find_all('tr') # find all rows in the table
    hdr = rows.pop(0).find_all('th') # find column headings
    assert hdr[0].text == u'Country or region:' # verify that first column contains the country or region
    assert hdr[1].text == u'City or district:' # verify that the second column contains the city or district
    for row in rows: # loop over all rows
        td = row.find_all('td') # get each cell
        country = td[0].text
        city = td[1].text
        add_location(continent, country, city, db)

# verify that only tables within a section are retrieved
def contains_headline(tag):
    return tag.find(class_='mw-headline') is not None

# main loop 
# initializes the data structure
# retrieves the page 
# locates the tables with locations
# saves parsed data
def main():
    db = [] # initialize data structure
    soup = BeautifulSoup(requests.get('https://en.wikipedia.org/wiki/List_of_Occupy_movement_protest_locations').text, 'xml') # request wiki page
    for th in soup.find_all('th', text=re.compile("Country")): # find column headings which contain 'country'
        table = th.find_parent('table') # locte table in which this column heading is found
        continent = table.find_previous_sibling(contains_headline).find(class_='mw-headline').findAll(text=True) # get section title, i.e. continent
        scan_table(table, continent, db)
        
    # Write out to the sqlite database using scraperwiki library
    scraperwiki.sqlite.save(unique_keys=['city'], data=db)

main()