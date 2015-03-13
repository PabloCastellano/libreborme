import time
import os
import datetime
from lxml import etree
import sys

if len(sys.argv) > 1:
    day = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    day = datetime.date.fromordinal(day.toordinal())
else:
    day = datetime.date(2014, 01, 02)

if len(sys.argv) > 2:
    end = datetime.datetime.strptime(sys.argv[2], '%Y%m%d')
    end = datetime.date.fromordinal(end.toordinal())
else:
    end = datetime.date.today()


if __name__ == '__main__':

    while day <= end:
        filename = "BORME-S-" + day.strftime('%Y%m%d') + ".xml"
        filename = os.path.join('xml', filename)
        print filename

        tree = etree.parse(filename)
        urls = tree.xpath('//urlPdf')
        fechasig = tree.xpath('/sumario/meta/fechaSig')[0].text
        fechasig = datetime.datetime.strptime(fechasig, '%d/%m/%Y')
        fechasig = datetime.date.fromordinal(fechasig.toordinal())

        for url in urls:
            filepdf = url.split('/')[-1]
            assert os.path.exists(filepdf)
            assert os.path.getsize(filepdf) == int(url.attrib['szBytes'])

        day = fechasig
        print 'sig:', str(fechasig)
        time.sleep(0.05)
