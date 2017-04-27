# -*- coding: UTF-8 -*-
#!/usr/bin/env python

import argparse
from collections import OrderedDict
import csv
import json
import os
from queue import Queue
import re
import sys
from threading import Thread, Lock
from time import sleep
from urllib.parse import urljoin

from lxml import html
import requests

__AUTHOR__ = "fuzzy69"
__VERSION__ = "0.0.1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:46.0) Gecko/20100101 Firefox/46.0"
}
HOST = "http://www.imdb.com/"
SEED_URL = urljoin(HOST, "/chart/top?ref_=nv_wl_img_3")

parser = argparse.ArgumentParser(description="IMDB Top 250 Scraper")
parser.add_argument("-c", action="store", dest="c", type=int, default=250, help="Number of items to scrape (min 1, max 250)")
parser.add_argument("-d", action="store", dest="d", type=int, default=1, help="Delay between requests in seconds")
parser.add_argument("-f", action="store", dest="f", type=str, default="", help="Output file")
parser.add_argument("-ft", action="store", dest="ft", type=str, default="json", help="Output file format (json, csv, sqlite)")
parser.add_argument("-t", action="store", dest="t", type=int, default=1, help="Thread count")
parser.add_argument("-p", action="store", dest="p", default=str, help="Use proxies from file (max threads <= proxies count)")
parser.add_argument("-mp", action="store_true", dest="mp", default=False, help="Download movie posters")
parser.add_argument("-v", action="version", version="{}".format(__VERSION__))
args = parser.parse_args()

q = Queue()
lock = Lock()
movies = []

print("Scraping movies urls ...")
response = requests.get(SEED_URL, headers=HEADERS)
if response.status_code != 200:
    sys.exit("Can\'t open main page!. Exiting ...")
dom = html.fromstring(response.text)
dom.make_links_absolute(HOST)
elements = dom.xpath('//td[@class="titleColumn"]//a')
for i, el in enumerate(elements):
    q.put(el.attrib["href"])
    if i > (args.c - 2) or i > 249:
        break

def download(url, file_path):
    response = requests.get(url, headers=HEADERS, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return True
    return None

def to_slug(text, delimiter='-', to_lower=True):
    if delimiter == '-':
        text = re.sub('[^\w\s-]', '', text).strip()
        if to_lower:
            text = text.lower()
        text = re.sub('\s+', delimiter, text)
        text = re.sub('\-+', '-', text)
    else:
        text = re.sub('[^\w\s_]', '', text).strip()
        if to_lower:
            text = text.lower()
        text = re.sub('\s+', delimiter, text)
        text = re.sub('_+', '_', text)
    return text

def extract_movie_data(i, q):
    while True:
        url = q.get()
        print('Scraping data from "{}" ...'.format(url))
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print("Failed. Skipping ...")
            q.task_done()
            return
        dom = html.fromstring(response.text)
        dom.make_links_absolute(HOST)
        data = OrderedDict()
        elements = dom.xpath('//a[contains(@href, "/chart/top?ref_=tt_awd")]//text()')
        data.update({"imdb_position": elements[0].split("#")[1].strip()}) if elements else data.update({"imdb_position": ""})
        elements = dom.xpath('//meta[@property="og:title"]/@content')
        data.update({"title": elements[0].split('(')[0].strip()}) if elements else data.update({"title": ""})
        elements = dom.xpath('//div[@itemprop="genre"]/a//text()')
        data.update({"genre": elements}) if elements else data.update({"genre": ""})
        elements = dom.xpath('//time/@datetime')
        duration = elements[0].strip() if elements else None
        if duration:
            matches = re.search(r'PT(\d+)M', duration)
            if matches:
                data.update({"duration": matches.group(1)})
        elements = dom.xpath('//div[@itemprop="description"]/p/text()')
        data.update({"story": '\n'.join(elements).strip()}) if elements else data.update({"story": ""})
        elements = dom.xpath('//span[@itemprop="director"]//span/text()')
        data.update({"director": elements}) if elements else data.update({"director": ""})
        elements = dom.xpath('//table[@class="cast_list"]//span[@itemprop="name"]//text()')
        data.update({"cast": elements}) if elements else data.update({"cast": ""})
        elements = dom.xpath('//a[starts-with(@href, "/country/")]//text()')
        data.update({"country": elements}) if elements else data.update({"country": ""})
        elements = dom.xpath('//a[starts-with(@href, "/language/")]//text()')
        data.update({"language": '\n'.join(elements[0].strip().split(','))}) if elements else data.update({"language": ""})
        elements = dom.xpath('//meta[@itemprop="datePublished"]/@content')
        data.update({"released": elements[0]}) if elements else data.update({"released": ""})
        if args.mp:
            elements = dom.xpath('//div[@class="poster"]//img/@src')
            if elements:
                download(elements[0], "data/" + to_slug(data["title"]) + ".jpg")
        with lock:
            movies.append(data)
        q.task_done()
        sleep(args.d)

for i in range(args.t):
    t = Thread(target=extract_movie_data, args=(i, q))
    t.setDaemon(True)
    t.start()

q.join()

if not args.f:
    print(json.dumps(movies, indent=4))
else:
    print("Writing to file ...")
    if args.ft == "csv":
        file_path = "data/" + args.f + ".csv"
        with open(file_path, "w") as f:
            w = csv.DictWriter(f, movies[0].keys())
            w.writeheader()
            w.writerows(movies)
    elif args.ft == "sqlite":
        pass
    else:
        # Default
        file_path = "data/" + args.f + ".json"
        with open(file_path, "w") as f:
            f.write(json.dumps(movies))

sys.exit("Done.")