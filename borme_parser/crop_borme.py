#!/usr/bin/env python
import logging
import os
import sys
import time

from pyPdf import PdfFileWriter, PdfFileReader

LOGFILE = 'cropborme.log'
DEFAULT_OUT_DIR = 'pdfcrop'
REWRITE = False  # Allows resuming

# Logs warnings, errors and criticals to stdout and file
logging.basicConfig(filename=LOGFILE, level=logging.WARNING, format='\n%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
logger = logging.getLogger("cropBORME")  # name

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.WARNING)
logger.addHandler(h1)

results = {'error': 0, 'skip': 0, 'ok': 0}


def cropPage(page, crop, rotate):
    # Note that the coordinate system is up-side down compared with Qt.
    x0, y0 = page.mediaBox.lowerLeft
    x1, y1 = page.mediaBox.upperRight
    x0, y0, x1, y1 = float(x0), float(y0), float(x1), float(y1)
    x0, x1 = x0 + crop[0] * (x1 - x0), x1 - crop[2] * (x1 - x0)
    y0, y1 = y0 + crop[3] * (y1 - y0), y1 - crop[1] * (y1 - y0)
    page.mediaBox.lowerLeft = (x0, y0)
    page.mediaBox.upperRight = (x1, y1)
    # Update CropBox as well
    page.cropBox.lowerLeft = (x0, y0)
    page.cropBox.upperRight = (x1, y1)
    if rotate != 0:
        page.rotateClockwise(rotate)


def usage():
    print "Usage: %s <directory|file> [directory|file]" % sys.argv[0]
    sys.exit(-1)


def cropDir(dirIn, dirOut):
    """
        Crop files in batch mode

        dirIn:
        dirOut:
    """
    gen = os.walk(dirIn)
    _, _, files = gen.next()
    total = len(files)

    for i, f in enumerate(files):
        filename = os.path.join(dirIn, f)
        filenameOut = f + "-cropped.pdf"
        filenameOut = os.path.join(dirOut, filenameOut)
        print "[%d/%d] Writing %s" % (i + 1, total, filenameOut),

        try:
            res = cropFile(filename, filenameOut)
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


def cropFile(filenameIn, filenameOut):
    """
        Crop file according to BORME PDF format

        filename:
        filenameOut:
    """

    if os.path.isdir(filenameOut):
        filenameOut = os.path.join(filenameOut, os.path.basename(filenameIn))

    if os.path.exists(filenameOut) and not REWRITE:
        logger.info('Skipping file %s already exists and rewriting is disabled!' % filenameOut)
        return False

    input1 = PdfFileReader(file(filenameIn, "rb"))
    output = PdfFileWriter()
    numPages = input1.getNumPages()

    # cabecera
    page = input1.getPage(0)
    # (x0, x1, y0, y1)
    crop = (0.08196721311475409, 0.26981300089047194, 0.09079445145018916, 0.0)
    cropPage(page, crop, False)
    output.addPage(page)

    crop = (0.0832282471626734, 0.11308993766696349, 0.08953341740226986, 0.03294746215494212)
    for i in range(1, numPages - 1):
        page = input1.getPage(i)
        cropPage(page, crop, False)
        output.addPage(page)

    # borde final
    crop = (0.0832282471626734, 0.11308993766696349, 0.08953341740226986, 0.053428317008014245)
    page = input1.getPage(numPages - 1)
    cropPage(page, crop, False)
    output.addPage(page)

    outputStream = file(filenameOut, "wb")
    output.write(outputStream)
    outputStream.close()

    return True


if __name__ == '__main__':
    start_time = time.time()

    if len(sys.argv) == 1:
        usage()

    filenameIn = sys.argv[1]
    if os.path.isdir(filenameIn):
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_DIR
        if os.path.isdir(filenameOut):
            cropDir(filenameIn, filenameOut)
        else:
            if filenameOut == DEFAULT_OUT_DIR:
                os.mkdir(DEFAULT_OUT_DIR)
                cropDir(filenameIn, filenameOut)
            else:
                print "If first parameter is a directory, second one must be too and exist"
                sys.exit(1)

    elif os.path.isfile(filenameIn):
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(filenameIn) + "-cropped.pdf"
        filenameOut = os.path.join(DEFAULT_OUT_DIR, filenameOut)
        print "[1/1] Writing", filenameOut,
        try:
            res = cropFile(filenameIn, filenameOut)
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
    print '\tCropped:', results['ok']
    print '\tSkipped:', results['skip']

    if results['error'] > 0:
        print '\tErrors:', results['error'], '(see %s for more information).' % LOGFILE
    else:
        print '\tErrors:', results['error']

    print '\tElapsed time: %.2f seconds' % elapsed_time
