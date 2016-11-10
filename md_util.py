from pyDir_util import *

H1 = '''# RAI PRODUCT PDF LIST
[TOCM]

[TOC]
'''


markdown = [H1]

groups = pdf_df.groupby(by='cata')

def makeH2(cata):
    return '\n## %s' % cata

def makeLink(name, url):
    return '[%s](%s)' % (name, url)


def makeH3(s):
    # each product use H3
    productName = s.productName
    body = []
    header = '\n### %s' % productName
    body.append(header)

    urls = s.pdfLinks
    for url in urls:
        file = url.split('/')[-1]
        link = makeLink(file, url)
        body.append('* ' + link)

    return '\n'.join(body)


def makeGroup(group):
    # each group use a H2
    body = []
    cata = group[0]
    body.append(makeH2(cata))

    df = group[1]
    for i in range(len(df)):
        s = df.iloc[i]
        h3 = makeH3(s)
        body.append(h3)

    return '\n'.join(body)


def makeContent(groups):
    body = []
    for group in groups:
        # each group use a H2
        group = makeGroup(group)
        body.append(group)

    return '\n'.join(body)


def dump_md(fn):
    md = makeContent(groups)
    md = H1+md
    with open(fn, 'wb') as f:
        f.write(md.encode())
