import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = 'BORME-A-2014-98-38.pdf'

# Open a PDF document.
fp = open(fname, 'rb')
parser = PDFParser(fp)
password=''
document = PDFDocument(parser, password)

# Get the outlines of the document.
outlines = document.get_outlines()
for (level,title,dest,a,se) in outlines:
    print (level, title)

# Outlines de nivel 2 son las empresas
