from bs4 import BeautifulSoup
from pprint import pprint as pp
from urllib import urlopen
from urlparse import urlparse


class Scrape(object):
    """docstring for Scrape"""
    def __init__(self, attributelist, url):
        self.url = url
        self.attributelist = attributelist
        self.attributepairs = {}
        self._getMetaData()

    def __getattr__(self, attr):
        """ tries to collect (if not collected before) and return webpage's attribute. If fails then 'Not found'"""
        if attr in self.attributepairs:
            return self.attributepairs[attr]
        raw_attr = self.soup.find(attr)
        if raw_attr and raw_attr.string:
            self.attributepairs[attr] = raw_attr.string.encode('utf-8')
            return self.attributepairs[attr]
        else:
            return '404 Error: Attribute Not Found'

    def __repr__(self):
        """ Nicely formatted dictionary """
        return '\n'.join(':\t'.join(i) for i in self.attributepairs.items())

    # try to get metadata from OG first before delving into content
    def _getMetaData(self):
        self.soup = BeautifulSoup(urlopen(self.url), 'html.parser')
        # get metatags first and construct empty dict to populate
        metatags = self.soup.find_all('meta')

        for metatag in metatags:
            if 'property' in metatag.attrs:
                # metatags begin with og:[[value]], so this
                # strips that component out to match against our list
                cleanedproperty = str(metatag.attrs['property'].replace('og:', ''))
                if cleanedproperty in self.attributelist:
                    propertycontent = metatag['content'].encode('utf-8')
                    self.attributepairs[cleanedproperty] = propertycontent

        # homogenize and find differences between lists
        # to see what still needs to be done
        remainingattributes = set(self.attributelist) - set(self.attributepairs.keys())

        if 'title' in remainingattributes:
            self.getTitle()

        if 'image' in remainingattributes:
            self.getImage()

        if 'site_name' in remainingattributes:
            self.getSiteName()

        if 'description' in remainingattributes:
            self.getDescription()


    # most websites have title tag, so if this metatag isn't fleshed out,
    # populate it manually
    def getTitle(self):
        self.attributepairs['title'] = self.title

    # upgrade this to images over a certain resolution
    # remember to filter by aspect ratio after NSFW-proofing
    def getImage(self):
        img = self.soup.find('img')['src']
        self.attributepairs['image'] = img

    # site base name should be found using regex or urlparse
    def getSiteName(self):
        # netloc is component of urlparse tuple
        # https://docs.python.org/2/library/urlparse.html
        site_name = urlparse(self.url).netloc
        self.attributepairs['site_name'] = site_name

    # if description unavailable, find first instance of p tag,
    # then span with at least 50 characters
    def getDescription(self):
        textbase = self.soup.find_all('p')
        try:
            description = next((text.string for text in textbase if len(text.string) > 50), 'No description found.')
        except:
            description = 'No description found.'
        self.attributepairs['description'] = description

    # metatag list:
    # title, type, name, image, url, audio, description, determiner, locale
    # locale:alternate, site_name, video, imageurl
attributelist = ['title', 'site_name', 'image', 'description']
url = 'http://www.reddit.com/r/learnpython/comments/3cxetk/hi_rlearnpython_a_few_questions_from_a_noobish/'
rdt = Scrape(attributelist, url)
print(rdt)
print(rdt.attributepairs)
