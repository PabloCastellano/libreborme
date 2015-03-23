#!/usr/bin/env python
import logging
import os
import sys
import time

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams


LOGFILE = 'borme.log'
DEFAULT_OUT_DIR = 'txt'
REWRITE = False  # Allows resuming

# Logs warnings, errors and criticals to stdout and file
logging.basicConfig(filename=LOGFILE, level=logging.WARNING, format='\n%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
logger = logging.getLogger("parseBORME")  # name

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.WARNING)
logger.addHandler(h1)

results = {'error': 0, 'skip': 0, 'ok': 0}


def parseDir(dirIn, dirOut):
    """
        Parse files in batch mode

        dirIn:
        dirOut:
    """
    gen = os.walk(dirIn)
    _, _, files = gen.next()
    total = len(files)

    for i, f in enumerate(files):
        filename = os.path.join(dirIn, f)
        filenameOut = f + ".1.txt"
        filenameOut = os.path.join(dirOut, filenameOut)

        print "[%d/%d] Writing %s" % (i + 1, total, filenameOut),
        filename = os.path.join(dirIn, f)
        try:
            res = parseFile(filename, filenameOut)
            if res:
                print "OK"
                results['ok'] += 1
            else:
                print "SKIP"
                results['skip'] += 1
        except:
            print "ERROR\n"
            logger.exception("Error processing file %s", filename)
            print
            results['error'] += 1


def parseFile(filenameIn, filenameOut):
    """
        Parse file according to BORME PDF format

        filename:
        filenameOut:
    """

    if os.path.isdir(filenameOut):
        filenameOut = os.path.join(filenameOut, os.path.basename(filenameIn))

    if os.path.exists(filenameOut) and not REWRITE:
        logger.info('Skipping file %s already exists and rewriting is disabled!' % filenameOut)
        return False

    # conf
    codec = 'utf-8'
    laparams = LAParams()
    imagewriter = None
    pagenos = set()
    maxpages = 0
    password = ''
    rotation = 0

    # <LAParams: char_margin=2.0, line_margin=0.5, word_margin=0.1 all_texts=False>
    laparams.detect_vertical = True
    laparams.all_texts = False
    laparams.char_margin = 2.0
    laparams.line_margin = 0.5
    laparams.word_margin = 0.1

    caching = True
    rsrcmgr = PDFResourceManager(caching=caching)
    outfp = file(filenameOut, 'w')
    device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams, imagewriter=imagewriter)
    fp = file(filenameIn, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # https://github.com/euske/pdfminer/issues/72
    #page = PDFPage()
    #PDFPage.cropbox =

    for page in PDFPage.get_pages(fp, pagenos,
                                  maxpages=maxpages, password=password,
                                  caching=caching, check_extractable=True):
        page.rotate = (page.rotate + rotation) % 360
        interpreter.process_page(page)
    fp.close()
    device.close()
    outfp.close()

    return True


def usage():
    print "Usage: %s <directory|file> [directory|file]" % sys.argv[0]
    sys.exit(-1)


if __name__ == '__main__':
    start_time = time.time()

    if len(sys.argv) == 1:
        usage()

    filenameIn = sys.argv[1]
    if os.path.isdir(filenameIn):
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_DIR
        if os.path.isdir(filenameOut):
            parseDir(filenameIn, filenameOut)
        else:
            if filenameOut == DEFAULT_OUT_DIR:
                os.mkdir(DEFAULT_OUT_DIR)
                parseDir(filenameIn, filenameOut)
            else:
                print "If first parameter is a directory, second one must be too and exist"
                sys.exit(1)

    elif os.path.isfile(filenameIn):
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(filenameIn) + '.1.txt'
        filenameOut = os.path.join(DEFAULT_OUT_DIR, filenameOut)
        print "[1/1] Writing", filenameOut,
        try:
            res = parseFile(filenameIn, filenameOut)
            if res:
                print "OK"
                results['ok'] += 1
            else:
                print "SKIP"
                results['skip'] += 1
        except:
            print "ERROR"
            logger.exception("Error processing file %s", filenameIn)
            results['error'] += 1
    else:
        logger.error("File %s doesn't exist" % filenameIn)

    elapsed_time = time.time() - start_time

    print '\nResults:'
    print '\tParsed:', results['ok']
    print '\tSkipped:', results['skip']

    if results['error'] > 0:
        print '\tErrors:', results['error'], '(see %s for more information).' % LOGFILE
    else:
        print '\tErrors:', results['error']

    print '\tElapsed time: %.2f seconds' % elapsed_time
