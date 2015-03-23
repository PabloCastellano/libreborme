#!/usr/bin/env python
import requests
import time
import os
import datetime
from lxml import etree
import sys

start_time = time.time()

# https
URL = 'http://www.boe.es'


def download_url(url):
    filename = url.split('/')[-1]
    filename = os.path.join('pdf', filename)

    if os.path.exists(filename):
        print filename, 'already exists. Skipped.'
        return False

    print url,
    r = requests.get(url, stream=True)
    cl = r.headers.get('content-length')
    print "%.2f KB" % (int(cl) / 1024.0)

    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(8192):
            fd.write(chunk)

    return True


if __name__ == '__main__':

    print 'Usage: %s [date_start] [date_end]'
    print '\tdate format: YEARmonthday (ex.: 20141014)'

    if len(sys.argv) > 1:
        day = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        day = datetime.date.fromordinal(day.toordinal())
    else:
        #day = datetime.date(2014, 01, 02)
        day = datetime.date.today()

    if len(sys.argv) > 2:
        end = datetime.datetime.strptime(sys.argv[2], '%Y%m%d')
        end = datetime.date.fromordinal(end.toordinal())
    else:
        end = datetime.date.today()

    total = 0
    while day <= end:
        filename = "BORME-S-" + day.strftime('%Y%m%d') + ".xml"
        filename = os.path.join('xml', filename)
        print filename

        tree = etree.parse(filename)
        items = tree.xpath('/sumario/diario/seccion/emisor/item')

        for item in items:
            url = URL + item.getchildren()[1].text
            converted = download_url(url)
            if converted:
                total += 1

        day = tree.xpath('/sumario/meta/fechaSig')[0].text
        if day is None:
            break

        day = datetime.datetime.strptime(day, '%d/%m/%Y')
        day = datetime.date.fromordinal(day.toordinal())
        print 'sig:', str(day)
        #time.sleep(0.05)

    elapsed_time = time.time() - start_time
    print 'End. Elapsed time:', elapsed_time, "seconds. Converted %d files." % total
