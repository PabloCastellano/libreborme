import requests
import time
import os
import datetime
from lxml import etree
import sys

start_time = time.time()

# https
URL = 'http://www.boe.es/diario_borme/xml.php?id=BORME-S-%s'



def download_url(url):
    filename = url.split('/')[-1]
    filename = os.path.join('pdf', filename)
    print url,

    r = requests.get(url, stream=True)
    cl = r.headers.get('content-length')
    print "%.2f KB" % (int(cl)/1024.0)

    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(8192):
            fd.write(chunk)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Usage: %s <ISO date>' % sys.argv[0]
        sys.exit(1)

    url = URL + sys.argv[1]
    download_url(url)

    print 'End.'
