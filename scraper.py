import scraperwiki # used for running the scraper and storing data
import requests # used for retrieving data
from bs4 import BeautifulSoup # used for parsing data
import re # used for regular expressions

# store results in structured format
def add_location(continent, country, city, db):
    print("%s\t%s\t%s"%(continent,country,city))
    db.append({
        'continent': continent.decode('utf-8'),
        'country': country.decode('utf-8'),
        'city': city.decode('utf-8')
    })

# parse table for locations
def parse_table(table, continent, db):
    # find all rows in the table
    rows = table.find_all('tr') 
    # find row with column headings
    hdr = rows.pop(0).find_all('th') 
    # if empty heading, get next row
    if hdr[1].text.strip() == '': 
        hdr = rows.pop(0).find_all('th')
    # verify that first column contains the country or region    
    assert re.match(r'Country|Province',hdr[0].text) 
    # verify that the second column contains the city or district
    assert re.match(r'City|Cities',hdr[1].text) 
    # initialize variables
    country = ""
    city = ""
    # loop over rows in the table
    for row in rows:
        # get each cell in this row
        td = row.find_all('td') 
        # remove line breaks
        td0_text = td[0].text.encode('utf8').replace("<br>"," ").replace("\n"," ").strip()
        td1_text = td[1].text.encode('utf8').replace("<br>"," ").replace("\n"," ").strip()
        # locate country and city columns (position may vary)
        if len(td) >= 6 and td[0].has_attr('rowspan'):
            country = td0_text
            city = td1_text
        elif len(td) == 6 and re.match(r'[0-9]',td1_text) is None and td1_text != "" and td0_text != "London":
            country = td0_text
            city = td1_text
        elif re.match(r'[0-9]',td1_text) is None:
            if country != td0_text:
                city = td0_text
            if country == td0_text:
                city = td1_text
        # remove things written after country names
        country = re.sub(r' - .*','',re.sub(r'organi.*','',country)).strip()
        # add to data structure
        add_location(continent, country, city, db)
    

# verify that only tables within a section are retrieved
def contains_headline(tag):
    return tag.find(class_='mw-headline') is not None

# main loop 
def main():
    # initialize data structure
    db = [] 
    # request wiki page
    html = requests.get('https://en.wikipedia.org/wiki/List_of_Occupy_movement_protest_locations').text 
    # load page as xml document
    soup = BeautifulSoup(html, 'xml') 
    # find column headings
    for th in soup.find_all('th'): 
        # retain headings with 'country'
        if re.match(r'Country|Province', th.text): 
            # locate table in which column heading is found
            table = th.find_parent('table')
            # only retain table which is associated with a section
            if table.find_previous_sibling(contains_headline):
                # get section title, i.e. continent
                continent = table.find_previous_sibling(contains_headline).find(class_='mw-headline').findAll(text=True)[0].encode('utf8')
                # parse table for country and city
                parse_table(table, continent, db)
        
    # Write results to the sqlite database using scraperwiki library
    scraperwiki.sqlite.save(unique_keys=['city'], data=db)

main()