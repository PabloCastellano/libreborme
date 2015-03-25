#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import os
import datetime
import sys
import logging

from borme_parser import get_borme_filename_xml, get_borme_xml_url, download_url

start_time = time.time()


#>>> datetime.date(2014, 10, 2) - datetime.date(2001, 01, 02)
#datetime.timedelta(5021)
# 502,1 / 60 / 2 = 4,18 min estimado
# Total real: 18 min, 199MB

#start: 20010102
# time elapsed
# bytes downloaded


LOGFILE = 'downloadxml.log'
LOGLEVEL = logging.INFO

logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format='%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
logger = logging.getLogger(__name__)

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(LOGLEVEL)
logger.addHandler(h1)

results = {'error': 0, 'skip': 0, 'ok': 0, 'warning': 0}


def download_pdf(day, end):
    while day <= end:
        url = get_borme_xml_url(day)
        xml_filename = get_borme_filename_xml(day)
        xml_filename = os.path.join('xml', xml_filename)
        logger.info('%s -> %s' % (url, xml_filename))
        try:
            downloaded = download_url(url, xml_filename)
            if downloaded:
                results['ok'] += 1
            else:
                logger.debug('%s already exists. SKIP.' % xml_filename)
                results['skip'] += 1
        except requests.exceptions.ConnectionError:
            logger.error('DOWNLOAD ERROR')
            results['error'] += 1

        day += datetime.timedelta(1)
        #time.sleep(0.05)


if __name__ == '__main__':

    print 'Usage: %s [date_start] [date_end]' % sys.argv[0]
    print '\tdate format: YEARmonthday (ex.: 20141014)'

    if len(sys.argv) > 1:
        day = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        day = datetime.date.fromordinal(day.toordinal())
    else:
        #day = datetime.date(2001, 01, 02)
        day = datetime.date.today()

    if len(sys.argv) > 2:
        end = datetime.datetime.strptime(sys.argv[2], '%Y%m%d')
        end = datetime.date.fromordinal(end.toordinal())
    else:
        end = datetime.date.today()

    download_pdf(day, end)

    elapsed_time = time.time() - start_time
    logger.info('End. Elapsed time: %s seconds. Downloaded %d files.' % (elapsed_time, results['ok']))

    logger.info('\nElapsed time: %.2f seconds' % elapsed_time)
    logger.info('Results:')
    logger.info('  Downloaded: %d' % results['ok'])
    logger.info('  Warning: %d' % results['warning'])
    logger.info('  Skipped: %d' % results['skip'])

    if results['error'] > 0:
        logger.info('  Errors: %d (see %s for more information).' % (results['error'], LOGFILE))
    else:
        logger.info('  Errors: %d' % results['error'])
