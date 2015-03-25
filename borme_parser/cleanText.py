#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import re


LOGFILE = 'bormecleantext.log'
DEFAULT_OUT_DIR = 'txt2'
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
        filenameOut = f + ".clean.txt"
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

    outfp = file(filenameOut, 'w')
    fp = file(filenameIn, 'r')

    # Al comienzo de una página nueva, el parser de PDF a texto añade el carácter 0x0c (^L)
    # y hace que no funcionen las expresiones regulares en estos casos.
    content = fp.read()
    content = re.sub(r"^\x0c(\d+)", "\\1", content, flags=re.M)
    content = re.sub(r"^\x0a\x0c(?!\d+)", "", content, flags=re.M)

    outfp.write(content)

    fp.close()
    outfp.close()

    return True


def usage():
    print "Usage: %s <directory|file> [directory|file]" % sys.argv[0]


if __name__ == '__main__':
    start_time = time.time()

    if len(sys.argv) == 1:
        usage()
        sys.exit(-1)

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
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(filenameIn) + '.clean.txt'
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
