#!/usr/bin/env python

import requests
import time
import os
import datetime
import sys

# Falla https
#URL = "https://www.boe.es/diario_borme/xml.php?id=BORME-S-"
URL = "http://www.boe.es/diario_borme/xml.php?id=BORME-S-"

#>>> datetime.date(2014, 10, 2) - datetime.date(2001, 01, 02)
#datetime.timedelta(5021)
# 502,1 / 60 / 2 = 4,18 min estimado
# Total real: 18 min, 199MB

#start: 20010102



# time elapsed
# bytes downloaded


def download_url(url):
    filename = "BORME-S-" + day.strftime('%Y%m%d') + ".xml"
    filename = os.path.join('xml', filename)

    if os.path.exists(filename):
        print filename, 'already exists. Skipped.'
        return False

    print url, '->', filename,
    r = requests.get(url, stream=True)

    cl = r.headers.get('content-length')
    print "%.2f KB" % (int(cl) / 1024.0)

    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(8192):
            fd.write(chunk)

    return True


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

    total_dl = 0
    while day <= end:
        fullurl = URL + day.strftime('%Y%m%d')
        downloaded = download_url(fullurl)
        if downloaded:
            total_dl += 1

        day += datetime.timedelta(1)
        time.sleep(0.05)

    print '\nEnd. Total files downloaded:', total_dl
