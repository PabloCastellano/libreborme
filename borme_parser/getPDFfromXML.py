#!/usr/bin/env python
import requests
import time
import os
import datetime
from lxml import etree
import sys
import logging

start_time = time.time()

# https
URL = 'http://www.boe.es'

LOGFILE = 'downloadpdf.log'
LOGLEVEL = logging.INFO

logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format='%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
logger = logging.getLogger(__name__)

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(LOGLEVEL)
logger.addHandler(h1)

results = {'error': 0, 'skip': 0, 'ok': 0, 'warning': 0}


def get_borme_filename_xml(day):
    return"BORME-S-" + day.strftime('%Y%m%d') + ".xml"


def download_url(url):
    pdf_filename = url.split('/')[-1]
    pdf_filename = os.path.join('pdf', pdf_filename)

    if os.path.exists(pdf_filename):
        logger.debug('%s already exists. SKIP.' % pdf_filename)
        results['skip'] += 1
        return False

    logger.info(url)
    try:
        r = requests.get(url, stream=True)
        cl = r.headers.get('content-length')
        print "%.2f KB" % (int(cl) / 1024.0)

        with open(pdf_filename, 'wb') as fd:
            for chunk in r.iter_content(8192):
                fd.write(chunk)
    except requests.exceptions.ConnectionError:
        logger.error('DOWNLOAD ERROR')
        results['error'] += 1
        return False

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
        filename = get_borme_filename_xml(day)
        filename = os.path.join('xml', filename)

        if not os.path.isfile(filename):
            logger.warning('%s NOT FOUND' % filename)
            results['warning'] += 1
            day += datetime.timedelta(days=1)
            continue

        tree = etree.parse(filename)
        items = tree.xpath('/sumario/diario/seccion/emisor/item')

        for item in items:
            url = URL + item.getchildren()[1].text
            downloaded = download_url(url)
            if downloaded:
                total += 1
                results['ok'] += 1

        day = tree.xpath('/sumario/meta/fechaSig')[0].text
        if day is None:
            break

        day = datetime.datetime.strptime(day, '%d/%m/%Y')
        day = datetime.date.fromordinal(day.toordinal())
        #print 'sig:', str(day)
        time.sleep(0.05)

    elapsed_time = time.time() - start_time
    logger.info('End. Elapsed time: %s seconds. Downloaded %d files.' %(elapsed_time, total))

    logger.info('\nElapsed time: %.2f seconds' % elapsed_time)
    logger.info('Results:')
    logger.info('  Downloaded: %d' % results['ok'])
    logger.info('  Warning: %d' % results['warning'])
    logger.info('  Skipped: %d' % results['skip'])

    if results['error'] > 0:
        logger.info('  Errors: %d (see %s for more information).' % (results['error'], LOGFILE))
    else:
        logger.info('  Errors: %d' % results['error'])
