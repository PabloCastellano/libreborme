import sys
import pyPdf

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = 'BORME-A-2014-98-38.pdf'

outfile = fname + '.2.txt'

pdf = pyPdf.PdfFileReader(file(fname, 'rb'))

with open(outfile, 'w') as fp:
    for n in range(pdf.getNumPages()):
        page = pdf.getPage(n)
        text = page.extractText().encode('utf-8')
        fp.write(text)
