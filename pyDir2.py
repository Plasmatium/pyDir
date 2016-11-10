from IPython.core.debugger import Tracer
from bs4 import BeautifulSoup as bs
from dig import *
import requests as req
import json
import re

set_trace = Tracer(colors='linux')
asset_url_entrance = 'http://www.emerson.com/dynamic/fragment/productassets/en-us/downloadAssetAsJson/'
liq_url = 'http://www.emerson.com/catalog/en-us/liquid-analysis#facet:&productBeginIndex:0&orderBy:&pageView:grid&minPrice:&maxPrice:&pageSize:&'
gas_url = 'http://www.emerson.com/catalog/en-us/gas-analysis#facet:&productBeginIndex:0&orderBy:&pageView:grid&minPrice:&maxPrice:&pageSize:&'
flam_url = 'http://www.emerson.com/catalog/en-us/flame-gas-detection#facet:&productBeginIndex:0&orderBy:&pageView:grid&minPrice:&maxPrice:&pageSize:&'

# liq_soup = get_soup(liq_url)
static_count = 0
err = []


def add_err(x):
    func = err.append
    func(x)


def get_navString_href(navString):
    tag = navString.parent
    while True:
        if tag.a is None:
            tag = tag.parent
        else:
            return tag.a['href']


def get_urls_by_string(soup, string):
    navStrings = soup.find_all(text=string)
    urls = [get_navString_href(navString) for navString in navStrings]
    return urls

# --------------specified--------------


def get_productPdfLinks(productAsset, lang):
    url = productAsset['assetUrl']
    productName = productAsset['productName']
    if url is None:
        add_err(productAsset)
        return

    raw_content = json.loads(req.get(url).text)

    global static_count
    print('-' * 16 + '%d\t' % static_count + '-' * 16)
    static_count += 1

    raw_assets = []
    print('Fetching asset: %s' % url)
    for L in lang:
        try:
            raw_assets.append(raw_content[L])
        except KeyError as err:
            print('This language is not in list: %s.' % err)

    if len(raw_assets) == 0:
        print('Error in fetching pdf links: %s' % productName)
        print('Only these languages are available: %s.' %
              list(raw_content.keys()))
        print('----Asset link: %s' % url)
        add_err(productAsset)
        return
    '''
    try:
        raw_assets = [raw_content[L] for L in lang]
    except KeyError as e:
        print('No This Language: %s!!!'%e)
        print('All languages will be fetched!')
        raw_assets = raw_content
    '''
    url_set = set()

    def pred(k, v):
        if k != 'downloadUrl':
            return False
        if 'product-data' not in v and 'manual' not in v:
            return False
        return True

    def collect_values(d, pred, set_add):
        if type(d) is dict:
            for k, v in d.items():
                if pred(k, v):
                    set_add('http:' + d[k])
                collect_values(d[k], pred, set_add)

        if type(d) is list:
            for value in d:
                collect_values(value, pred, set_add)

    collect_values(raw_assets, pred, url_set.add)
    result = {'pdfLinks': list(url_set)}
    result.update(productAsset)

    return result
