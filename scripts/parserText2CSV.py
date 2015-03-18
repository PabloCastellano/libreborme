#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time

DEBUG = False
LOGFILE = 'bormecsv.log'
DEFAULT_OUT_DIR = 'csv'
REWRITE = False  # Allows resuming

# Logs warnings, errors and criticals to stdout and file
logging.basicConfig(filename=LOGFILE, level=logging.INFO, format='\n%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
logger = logging.getLogger("csvBORME")  # name

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.INFO)
logger.addHandler(h1)

results = {'error': 0, 'skip': 0, 'ok': 0}
csvline = {}

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
        filenameOut = f + ".1.csv"
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

def saveField(content):
    global csvline

    if DEBUG:
        print 'Guardando', content

    csvline[content[0]] = content[1]

    if not csvline.has_key('total'):
        csvline['total'] = 1
    else:
        csvline['total'] += 1


def printCSVHeader(outfp):
    line = ""
    for k in ("ID","Nombre","Modificaciones estatutarias","Sociedad unipersonal","Extinción","Disolución","Cambio de identidad del socio único","Nombramientos","Ceses/Dimisiones","Revocaciones","Reducción de capital","Datos registrales"):
        line += '"' + k + '",'
    outfp.write(line[:-1])
    outfp.write('\n')


def printCSVLine(outfp):
    global csvline

    if DEBUG:
        print 'Keys:', csvline.keys(), 'total:', csvline['total']

    line = ""
    # print CSV-friendly
    for k in ("ID","Nombre","Modificaciones estatutarias","Sociedad unipersonal","Extinción","Disolución","Cambio de identidad del socio único","Nombramientos","Ceses/Dimisiones","Revocaciones","Reducción de capital","Datos registrales"):
        if csvline.has_key(k):
            content = '"' + csvline[k].replace('"', '\\"') + '"'
            print content,
            line += content
        print ',',
        line += ','
    print
    line = line[:-1] + '\n'
    outfp.write(line)


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

    global csvline

    # regexp
    fp = open(filenameIn, 'r')
    text = fp.read()
    fp.close()

    outfp = open(filenameOut, 'w')
    printCSVHeader(outfp)
    # TODO: Compilar las regexp para mayor eficiencia
    # http://stackoverflow.com/questions/16720541/python-string-replace-regular-expression
    # regexp = re.compile(...)
    # m = regexp.findal(...)

    for trozo in text.split('.\n\n'):
        csvline = {}

        trozo += '.'

        # ['Modificaciones estatutarias.  Modificaci\xc3\xb3n del art. 27\xc2\xba de los estatutos en orden a la retribuci\xc3\xb3n del \xc3\xb3rgano de administraci\xc3\xb3n.- .', 'Datos registrales. T 2579 , F 215, S 8, H PM 74389, I/A 2 (22.01.15)']
        tr2 = trozo.split('\n')[1:]
        #tr2_ = ''.join(tr2)

        # Modificaciones estatutarias.  Modificación del art. 27º de los estatutos en orden a la retribución del órgano de administración.- . Datos registrales. T 2579 , F 215, S 8, H PM 74389, I/A 2 (22.01.15)
        tr2_ = ' '.join(tr2)

        if DEBUG:
            print trozo
            print tr2_

        m = re.match('(\d+) - (.*)\.\n', trozo)

        saveField(('ID', m.group(1)))
        saveField(('Nombre', m.group(2)))

        m = re.findall('(Reelecciones|Declaración de unipersonalidad|Nombramientos|Revocaciones|Ceses/Dimisiones|Constitución)\.\s+(.*?):\s+(.*?)\.', tr2_)

        #BORME-A-2014-88-25.pdf
        # Disolución. Voluntaria.

        if m != []:
            for algo in m:
                #print algo
                saveField(algo)

        m = re.findall('(Datos registrales)\.\s+(.*)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                saveField(algo)

        # FIXME: Determinar cuándo acaba el texto (con puntos en medio) de las modificaciones estatutarias.
        m = re.findall('(Modificaciones estatutarias)\.\s+(.*?)\.\s*(?:Datos registrales|Cambio de objeto social)', tr2_)
        if m != []:
            for algo in m:
                #print algo
                saveField(algo)

        m = re.findall('(Cambio de denominación social|Cambio de domicilio social|Ampliacion del objeto social)\.\s+(.*?)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                saveField(algo)

        m = re.findall('(Cambio de identidad del socio único|TEST):\s+(.*?)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                saveField(algo)

        m = re.findall('(Sociedad unipersonal|Extinción)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                saveField((algo, 'X'))

        if DEBUG:
            print '###########'
        printCSVLine(outfp)
        if DEBUG:
            print '###########'

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
        filenameOut = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(filenameIn) + '.1.csv'
        filenameOut = os.path.join(DEFAULT_OUT_DIR, filenameOut)
        logger.info('[1/1] Writing %s' % filenameOut)
        try:
            res = parseFile(filenameIn, filenameOut)
            if res:
                logger.info('OK')
                results['ok'] += 1
            else:
                logger.info('SKIP')
                results['skip'] += 1
        except:
            logger.info('ERROR')
            logger.exception("Error processing file %s", filenameIn)
            results['error'] += 1
    else:
        logger.error("File %s doesn't exist" % filenameIn)

    elapsed_time = time.time() - start_time

    logger.info('\nElapsed time: %.2f seconds' % elapsed_time)
    logger.info('Results:')
    logger.info('  Parsed: %d' % results['ok'])
    logger.info('  Skipped: %d' % results['skip'])

    if results['error'] > 0:
        logger.info('  Errors: %d (see %s for more information).' % (results['error'], LOGFILE))
    else:
        logger.info('  Errors: %d' % results['error'])
