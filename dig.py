from bs4 import BeautifulSoup as bs
import requests as req

import gevent
from gevent.monkey import patch_all

from selenium import webdriver

patch_all(thread=False)

def get_soup(url):
    resp = req.get(url)
    soup = bs(resp.content, 'lxml')
    return soup


def get_productInfo(tag):
    productName = tag.a.string
    productUrl = tag.a['href']
    return {'name': productName, 'url': productUrl}


def get_asset(productInfo):
    print('Starting processing product: %s' % productInfo['name'])
    product_soup = get_soup(productInfo['url'])
    asset_tag = product_soup.find(class_='cm-product-download-assets')

    if asset_tag == None:
        print('asset_tag is None: %s' % productInfo)
        assetUrl = None
        cata = Id = None
    else:
        url = asset_tag['data-json-cm-fragment']
        assetUrl = 'http:' + url
        cata, Id = url.split('/')[-2:]

    return {'productName': productInfo['name'],
            'assetUrl': assetUrl,
            'cata': cata,
            'Id': Id,
            'productUrl': productInfo['url']}


def get_productAsset(tag):
    productInfo = get_productInfo(tag)
    productAsset = get_asset(productInfo)
    return productAsset


def get_assets_links(productsList_url):
    print('-' * 8)
    w = webdriver.PhantomJS()
    w.get(productsList_url)
    page = w.page_source
    w.quit()
    products_list_page = bs(page)
    products = products_list_page.find_all(
        class_='product_name', id=lambda x: x != 'shoppingListItemAddedName')

    g = [gevent.spawn(get_productAsset, tag=tag_) for tag_ in products]
    results = gevent.joinall(g, timeout=30000)
    print('[][][][][][][][]Assets fetched: %s' % productsList_url)
    print('[][][][][][][][]')
    return [r.value for r in results]
