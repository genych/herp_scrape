from bs4 import BeautifulSoup
from pprint import pprint as pp
from urllib import urlopen
from urlparse import urlparse

#try to get metadata from OG first before delving into content
def getMetaData(attributelist, url):

    soup = BeautifulSoup(urlopen(url), 'html.parser')

    #get metatags first and construct empty dict to populate
    metatags = soup.find_all('meta')
    attributepairs = {}

    for metatag in metatags:
        if 'property' in metatag.attrs:
            #metatags begin with og:[[value]], so this strips that component out to match against our list
            cleanedproperty = str(metatag.attrs['property'].replace('og:',''))
            if cleanedproperty in attributelist:
                propertycontent = metatag['content'].encode('utf-8')
                attributepairs[cleanedproperty] = propertycontent

    #homogenize and find differences between lists to see what still needs to be done
    remainingattributes = set(attributelist) - set(attributepairs.keys())

    if 'title' in remainingattributes:
        getTitle(attributepairs,soup)

    if 'image' in remainingattributes:
        getImage(attributepairs,soup)

    if 'site_name' in remainingattributes:
        getSiteName(attributepairs,soup, url)

    if 'description' in remainingattributes:
        getDescription(attributepairs,soup)

    return attributepairs

#most websites have title tag, so if this metatag isn't fleshed out, populate it manually
def getTitle(attributepairs, soup):
    title = soup.find('title').string
    attributepairs['title'] = title

#upgrade this to images over a certain resolution
#remember to filter by aspect ratio after NSFW-proofing
def getImage(attributepairs, soup):
    img = soup.find('img')['src']
    attributepairs['image'] = img

#site base name should be found using regex or urlparse
def getSiteName(attributepairs,soup,url):
    #netloc is component of urlparse tuple - https://docs.python.org/2/library/urlparse.html
    site_name = urlparse(url).netloc
    attributepairs['site_name'] = site_name

#if description unavailable, find first instance of p tag, then span with at least 50 characters
def getDescription(attributepairs,soup):
    textbase = soup.find_all('p')
    try:
        description = next((text.string for text in textbase if len(text.string) > 50), 'No description found.')
    except:
        description = 'No description found.'
    attributepairs['description'] = description

#metatag list:
#title, type, name, image, url, audio, description, determiner, locale, locale:alternate
#site_name, video, imageurl
attributelist = ['title','site_name','image','description']
url = 'http://google.com'
pp(getMetaData(attributelist,url))

#pretty print test-result
#pp(getOGMetaData(attributelist,url))
