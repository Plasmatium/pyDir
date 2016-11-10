import gevent
import itertools as it
from pyDir2 import *

from gevent.monkey import patch_all
patch_all(thread=False)

orig_urls = []
orig_urls.append(liq_url)
orig_urls.append(liq_url.replace('Index:0', 'Index:23'))
orig_urls.append(liq_url.replace('Index:0', 'Index:46'))

orig_urls.append(gas_url)
orig_urls.append(gas_url.replace('Index:0', 'Index:23'))
orig_urls.append(gas_url.replace('Index:0', 'Index:46'))

orig_urls.append(flam_url)


def fetch_pdf_links(orig_url, lang):
	productAssets = get_assets_links(orig_url)

	g = [gevent.spawn(get_productPdfLinks, productAsset=asset, lang=lang) for asset in productAssets]
	results = gevent.joinall(g)

	return [result.value for result in results]


def fetch_all_pdf_links(lang=['Chinese', 'English']):
	g = [gevent.spawn(fetch_pdf_links, orig_url=url_set, lang=lang)
		 for url_set in orig_urls]
	results = gevent.joinall(g)
	results = [r.value for r in results]
	return list(it.chain(*results))
