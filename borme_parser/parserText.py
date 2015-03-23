#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time

LOGFILE = 'bormetext.log'
DEFAULT_OUT_DIR = 'txt2'
REWRITE = False  # Allows resuming

# Logs warnings, errors and criticals to stdout and file
logging.basicConfig(filename=LOGFILE, level=logging.WARNING, format='\n%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
logger = logging.getLogger("txtBORME")  # name

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
        filenameOut = f + ".1.reg"
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

    # regexp
    fp = open(filenameIn, 'r')
    text = fp.read()
    fp.close()

    #aes2 = re.findall('\d{6,} -', text)
    #re.findall('\d+ - .*?\n', text)
    #re.findall('\d{6,} - .*?\n', text)
    #aes = text.split('\n\n')
    #re.findall('\d{6}.*\.\n\n', text, re.X | re.S)
    #m = re.match('(\d+) - (.*)\n', results[17])
    #print '\n----------------------------------------------------\n'.join(aes)

    #results = re.findall('\d{6}.*?\.\n\n', text, re.X | re.S)
    #results = text.split('.\n\n')
    #r14 = results[14]
    #r141 = r14.split('\n')[0]
    #r142 = r14.split('\n')[1:]
    #r142_ = ''.join(r142)

    #re.findall('[Nombramientos\.|Ceses/Dimisiones\.]+\s+(.*?):\s+(.*?)\.', r142_)
    # re.findall('[[Nombramientos|Ceses/Dimisiones]\.\s+(.*?):\s+(.*?)\.|Modificaciones estatuarias\.\s+(.*?)\.]', r142_)
    #re.findall('[Modificaciones estatutarias|Cambio de denominación social|Cambio de domicilio social|Ampliacion del objeto social]\.\s+(.*?)\.\s+', r142_)

    #m = re.findall('\s+((Nombramientos\.|Ceses/Dimisiones\.)\s+(.*?):\s+(.*?)\.|(Modificaciones estatutarias|Cambio de denominación social|Cambio de domicilio social|Ampliacion del objeto social)\.\s+(.*?)\.\s+)', r142_)
    #m = re.findall('\s+((Nombramientos\.|Ceses/Dimisiones\.)\s+(.*?):\s+(.*?)\.|(Modificaciones estatutarias|Cambio de denominación social|Cambio de domicilio social|Ampliacion del objeto social)\.\s+(.*?)\.\s+)', r142_)
    #m = re.findall('\s+((Nombramientos|Ceses/Dimisiones)\s+(.*?):\s+(.*?)\.|(Modificaciones estatutarias|Cambio de denominación social|Cambio de domicilio social|Ampliacion del objeto social)\.\s+(.*?)\.\s+)', r142_)

    """
    print m
    print "3)"
    print r142_
    print
    for algo in m:
        #print algo
        print algo[1:]

    idborme, empresa = m.group(1), m.group(2)
    print idborme
    print empresa
    """

    for trozo in text.split('.\n\n'):

        # fix: a veces al final hay este caracter
        if trozo == '\x0c':
            continue

        tr1 = trozo.split('\n')[0]
        tr2 = trozo.split('\n')[1:]
        #tr2_ = ''.join(tr2)
        tr2_ = ' '.join(tr2)

        print "0)"
        m = re.match('(\d+) - (.*)\.\n', trozo)
        print m.group(1)
        print m.group(2)

        m = re.findall('(Reelecciones|Declaración de unipersonalidad|Nombramientos|Revocaciones|Ceses/Dimisiones|Constitución)\.\s+(.*?):\s+(.*?)\.', tr2_)

        #BORME-A-2014-88-25.pdf
        # Disolución. Voluntaria.
        print
        print "1)"
        for algo in m:
            print algo

        # Falta: Datos registrales
        print "2)"
        m = re.findall('(Datos registrales|Modificaciones estatutarias|Cambio de denominación social|Cambio de domicilio social|Ampliacion del objeto social)\.\s+(.*?)\.\s*', tr2_)
        for algo in m:
            print algo

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
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(filenameIn) + '.1.reg'
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
