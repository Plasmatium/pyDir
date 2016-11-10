from concurrent_fetch import *
import pandas as pd
import json
import requests as req
import os

with open('links/PDF2.orig', 'rb') as f:
    j = json.loads(f.read().decode())

pdf_df = pd.DataFrame(j)


def search_link_by_string(string):
    index = [string in name for name in pdf_df.productName]
    return pdf_df[index]


def download(productName, pdfUrl):

    dirName = productName
    fileName = pdfUrl.split('/')[-1]
    try:
        os.mkdir(dirName)
    except FileExistsError:
        pass

    print('-'*16 + 'Downloading!' + '-'*16)
    print(fileName)
    print()

    filedata = req.get(pdfUrl).content
    with open('/'.join([dirName, fileName]), 'wb') as f:
        f.write(filedata)

    # download._count and download._total should
    # be assiagned in batchDownload() where download()
    # would be called
    download._count += 1
    percentage_val = download._count/download._total*100
    print('-'*16 + 'Done! %d%%'%percentage_val + '-'*16)
    print(fileName)
    print()


def batchDownload(df):
    dataDict = df.to_dict('index')
    g = []

    for k, v in dataDict.items():
        # download(v.productName, url) for url in v.pdfLinks
        for url in v['pdfLinks']:
            g.append(
                gevent.spawn(download, productName=v['productName'], pdfUrl=url))

    download._count = 0
    download._total = len(g)
    print('====Total file count: %d====' % download._total)

    results = gevent.joinall(g)
    return results
