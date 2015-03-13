#!/usr/bin/env python
import os
import sys
import time

from pyPdf import PdfFileWriter, PdfFileReader

DEFAULT_OUT_DIR = 'pdfcrop'
REWRITE = True


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
    gen = os.walk(dirIn)
    _, _, files = gen.next()

    for f in files:
        filename = os.path.join(dirIn, f)
        cropFile(filename, dirOut)


def cropFile(filename, filenameOut):
    print filename
    input1 = PdfFileReader(file(filename, "rb"))

    output = PdfFileWriter()
    numPages = input1.getNumPages()

    """
    page = input1.getPage(0)
    page.mediaBox.lowerLeft = (40, 40)
    page.mediaBox.upperRight = (550, 610)
    page.cropBox.lowerLeft = (40, 40)
    page.cropBox.upperRight = (550, 610)
    output.addPage(page)

    for i in range(1, numPages):
        page = input1.getPage(i)
        print page.mediaBox.getUpperRight_x(), page.mediaBox.getUpperRight_y()
    #    page.trimBox.lowerLeft = (40, 40)
    #    page.trimBox.upperRight = (550, 735)
        page.mediaBox.lowerLeft = (40, 40)
        page.mediaBox.upperRight = (550, 735)
        page.cropBox.lowerLeft = (40, 40)
        page.cropBox.upperRight = (550, 735)
        print page
        output.addPage(page)
    """

    # cabecera
    page = input1.getPage(0)
    # (x0, x1, y0, y1)
    crop = (0.08196721311475409, 0.26981300089047194, 0.09079445145018916, 0.0)
    cropPage(page, crop, False)
    output.addPage(page)
    crop = (0.0832282471626734, 0.11308993766696349, 0.08953341740226986, 0.03294746215494212)

    for i in range(1, numPages - 1):
        print "%d/%d" % (i, numPages)
        page = input1.getPage(i)
        cropPage(page, crop, False)
        output.addPage(page)

    # borde final
    #crop = (0.08575031525851198, 0.2840605520926091, 0.08448928121059268, 0.053428317008014245)
    #crop = (0.08575031525851198, 0.12288512911843277, 0.08448928121059268, 0.053428317008014245)
    crop = (0.0832282471626734, 0.11308993766696349, 0.08953341740226986, 0.053428317008014245)
    page = input1.getPage(numPages - 1)
    cropPage(page, crop, False)
    output.addPage(page)

    if os.path.isdir(filenameOut):
        filenameOut = os.path.join(filenameOut, os.path.basename(filename))

    if os.path.exists(filenameOut) and not REWRITE:
        print 'Warning: %s already exists! Skipping' % filenameOut

    outputStream = file(filenameOut, "wb")
    output.write(outputStream)
    outputStream.close()


if __name__ == '__main__':
    start_time = time.time()

    if len(sys.argv) == 1:
        usage()

    filename = sys.argv[1]
    if os.path.isdir(filename):
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_DIR
        if os.path.isdir(filenameOut):
            cropDir(filename, filenameOut)
        else:
            print "If first parameter is a directory, second one must be too and exist"
            sys.exit(1)

    elif os.path.isfile(filename):
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else filename + "-cropped.pdf"
        cropFile(filename, filenameOut)
    else:
        print "File %s doesn't exist" % filename

    elapsed_time = time.time() - start_time
    print 'End. Elapsed time:', elapsed_time
