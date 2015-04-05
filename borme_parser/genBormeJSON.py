#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Importar con mongoimport
# cat xmljson/*.json | mongoimport -d libreborme -c borme --jsonArray --upsert --upsertFields name

# TODO: Hacer un unico json con todo agregado
# OJO: Changed in version 2.2: The limit on document size increased from 4MB to 16MB.

import re
import sys
import logging
import getopt
from lxml import etree
import datetime
import json

from borme_parser import *


class XML1LBCommonParser(LBCommonParser):

    LOGFILE = 'bormexml.log'
    DEFAULT_OUT_DIR = 'xmljson'
    REWRITE = True  # Allows resuming
    CSV = False
    NAME = 'x1'

    def get_filename_out(self, basename):
        return "%s.%s.json" % (basename, self.NAME)

    def parse_file(self, filenameIn, filenameOut):
        """
            Parse file according to BORME PDF format

            filename:
            filenameOut:
        """

        #had_warning = False

        #if os.path.isdir(filenameOut):
        #    filenameOut = os.path.join(filenameOut, os.path.basename(filenameIn))

        if os.path.exists(filenameOut) and not self.REWRITE:
            self.logger.info('Skipping file %s already exists and rewriting is disabled!' % filenameOut)
            return False

        tree = etree.parse(filenameIn)

        year = tree.xpath('/sumario/meta/anno')[0].text
        fecha = tree.xpath('/sumario/meta/fecha')[0].text
        #fecha = datetime.datetime.strptime(fecha, '%d/%m/%Y')

        secciones = tree.xpath('/sumario/diario/seccion')
        for seccion in secciones:
            cod_seccion = seccion.get('num') # A, B, C
            items = seccion.xpath('emisor/item')
            for item in items:
                nombre = item.get('id') # 'BORME-A-2014-195-01'
                provincia = item.find('titulo').text # ARABA/ALAVA
                url = URL_BASE + item.getchildren()[1].text # http://www.boe.es/borme/dias/2014/10/13/pdfs/BORME-A-2014-195-01.pdf

                # Nombre completo, Tipo, Año, Nº, Provincia, cod_provincia, Fecha, URL?
                d = {'name': nombre, 'type': cod_seccion, 'year': year, 'provincia': provincia,
                     'date': fecha, 'url': url}

                #d['cod_provincia'] = POSTAL_REVERSE[provincia]
                # AQUI: hacer un json o añadir a MongoDB

                filenameOut = self.get_filename_out(nombre)
                filenameOut = os.path.join(self.DEFAULT_OUT_DIR, filenameOut)
                with open(filenameOut, 'w') as outfp:
                    outfp.write(json.dumps(d, sort_keys=True, indent=4))

        #if had_warning:
        #    self.results['error'] += 1

        return True


def usage():
    print "Usage: %s [-c|-v] <IN:directory|file> [OUT:directory|file]" % sys.argv[0]


if __name__ == '__main__':

    """
    try:
        (options, arguments) = getopt.getopt(sys.argv[1:], "cv", ['version'])
    except getopt.GetoptError, msg:
        usage()
        sys.exit(-1)
    """

    if len(sys.argv) == 1:
        usage()
        sys.exit(-1)

    logging_level = logging.INFO
    csv_format = True

    """
    for (switch, val) in options:
        if switch == '-v':
            logging_level = logging.DEBUG
        elif switch == '-c':
            csv_format = True
        elif switch == '--version':
            print "parser v0.4"
            sys.exit(0)
    """

    #parser = XML1LBCommonParser(logging.DEBUG)
    parser = XML1LBCommonParser(logging_level, csv_format)
    parser.main(sys.argv)
    parser.show_stats()
