from pipe import *
from bs4 import BeautifulSoup
import requests
import ipdb
import os
import time

rqhd = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Host':'www2.emersonprocess.com',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'}
hoststr = 'http://' + rqhd['Host']



firstlink = r'http://www2.emersonprocess.com/en-US/brands/rosemountanalytical/Pages/index.aspx'

##################################################################################
# get part_links
def get_main_links():

	r = requests.get(firstlink)
	soup = BeautifulSoup(r.content, "lxml")
	h2 = soup('h2')
	linkdata = (h2[1].parents|as_list)[1]('a')|select(lambda x: x.get('href'))\
	|select(lambda x: 'http://' in x and x or hoststr + x)

	main_links = linkdata|select(lambda x: (x, '/'.join(x.split('/')[6:])+'/'))

	return main_links


##############################################################################3
pdf_links = []
visited_links = []
total_pdf_num = 0
t_sleep = 0
def get_pdf_link(linkdata):
	#flow ctrl using time.sleep
	global t_sleep
	t_sleep += 1
	if t_sleep > 6:
		t_sleep = 0
		print('-'*10, ' sleep 0.6s ', '-'*10)
		time.sleep(0.6)

	#handle linkdata
	link = linkdata[0]
	path = linkdata[1]


	page = requests.get(link, headers=rqhd)
	print(page)
	print('fetched: %s' % link)
	global visited_links
	visited_links += [link]
	soup = BeautifulSoup(page.content, "lxml")
	#ipdb.set_trace()
	g_sub_links = soup('a')|where(lambda x: path in str(x.get('href')))
	# exclude link pointed to self & not in visited
	g_sub_links = g_sub_links|where(lambda x: rgexp_link(x['href']) != link)
	g_sub_links = g_sub_links|where(lambda x: rgexp_link(x['href']) not in visited_links)|as_list
	g_pdf_links = soup('a')|where(lambda x: 'pdf' in str(x.get('href')))

	#found right pdf tag
	right_pdf_links = g_pdf_links|where(lambda x: 'Product Data' in str(x.string)\
		or 'Manual' in str(x.string))\
	|select(lambda x: x['href']|Pipe(rgexp_link))|as_list
	if len(right_pdf_links) != 0:
		#ipdb.set_trace()
		global pdf_links
		pdf_links += [(path, right_pdf_links)]
		cur_pdf_num = len(right_pdf_links)
		print('pdf_links num +=: %d'%cur_pdf_num)
		global total_pdf_num
		total_pdf_num += cur_pdf_num
		print('total_pdf_num = %d'%total_pdf_num)

	#recursive search
	for tag in g_sub_links:
		if 'pdf' in str(tag['href']):
			continue
		#handle link ifrelative
		next_link = tag.get('href')
		next_link = rgexp_link(next_link)
		# exclude visited links
		if next_link in visited_links:
			continue
		path = '/'.join(next_link.split('/')[6:])+'/'
		
		#### condition bp #######
		#if 'Chlorine' in next_link:
			#ipdb.set_trace()
		get_pdf_link((next_link, path))


def rgexp_link(link):
	link = 'http://' in link and link or \
	hoststr + (link[0] == '/' and link or '/'+link)
	link = 'Pages/index.aspx' not in link and link or link[:-17] #cut 'Pages/index.aspx'
	return link

###########################################################################
t_sleep = 0
def fetch_pdf(pdf_link_items):
	fetched_pdf_links = []
	#flow ctrl using time.sleep
	global t_sleep
	t_sleep += 1
	if t_sleep > 6:
		t_sleep = 0
		print('-'*10, ' sleep 0.6s ', '-'*10)
		time.sleep(0.6)

	#item[0]: dir to write
	#item[1]: links
	#ipdb.set_trace()
	for item in pdf_link_items:
		#1 create dir
		dir = 'pdf/' + item[0]
		try:
			os.makedirs(dir)
		except FileExistsError:
			pass

		#2 create pdf file
		for link in item[1]:
			#first get filename, second fetch content, third write into file
			#1
			bn = link.split('/')[-1]
			fn = dir + bn
			print('handling file: %s' % bn)
			#exclude fetched files
			if link in fetched_pdf_links:
				print('file already fetched %s'%bn)
				continue
			if os.path.isfile(fn):
				print("file already fetched before %s"%fn)
				continue
			#2
			r = requests.get(link, headers=rqhd)
			#3
			f = open(fn, 'bw')
			f.write(r.content)
			f.close()
			print('file: %s fetched, in dir: %s' % (bn, dir))
			fetched_pdf_links += [link]

	return fetched_pdf_links
########################################################################
def update_links():
	main_links = get_main_links()
	for linkdata in main_links:
		get_pdf_link(linkdata)

	log = fetch_pdf(pdf_links)
	
	f = open('pdf/fetched.log', 'w')
	f.writelines(log)
	f.close()

def search_link(string, links):
	for link in links:
		if string in link[0]:
			print('found %s in\n %s'%(string, link))
			return [link]

	print('%s, not found'%string)

# =======================================
# fuzz match
from fuzzywuzzy import fuzz
from itertools import count as ct
import re
def match5(kw, links):
	result = []
	for linkset in links:
		files = linkset[1]|select(lambda x: x.split('/')[-1])
		for fn in files:
			words = re.split('[_-]', fn)
			lrat = 0
			cur_res = []
			for word in words:
				rat = fuzz.ratio(kw.upper(), word.upper())
				if rat <= lrat:
					continue
				lrat = rat
				cur_res = [(lrat, fn)]
			result += cur_res
	return ct(1)|izip(result|sort(key=lambda x: x[0],reverse=True)|take(5))|as_list

