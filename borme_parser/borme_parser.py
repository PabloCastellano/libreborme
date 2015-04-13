#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import unicodedata
import requests
import json
from bson import BSON
# import csv


def remove_accents(str):
    return ''.join((c for c in unicodedata.normalize('NFKD', unicode(str, 'utf-8')) if unicodedata.category(c) != 'Mn'))

# Falla https
#BORME_XML_URL = "https://www.boe.es/diario_borme/xml.php?id=BORME-S-"
BORME_XML_URL = "http://www.boe.es/diario_borme/xml.php?id=BORME-S-"

# Palabras clave con argumentos
ARG_KEYWORDS = ['Nombramientos', 'Revocaciones', 'Ceses/Dimisiones', 'Modificaciones estatutarias', 'Cambio de objeto social',
                'Cambio de denominación social', 'Cambio de domicilio social', 'Ampliacion del objeto social',
                'Sociedad unipersonal', 'Disolución', 'Reelecciones', 'Constitución',
                'Articulo 378.5 del Reglamento del Registro Mercantil', 'Otros conceptos',
                'Ampliación de capital', 'Reducción de capital', 'Situación concursal', 'Fusión por absorción',
                'Suspensión de pagos', 'Transformación de sociedad', 'Cancelaciones de oficio de nombramientos',
                'Desembolso de dividendos pasivos', 'Página web de la sociedad',
                'Primera sucursal de sociedad extranjera']

# Palabras clave sin argumentos
NOARG_KEYWORDS = ['Sociedad unipersonal', 'Extinción', 'Declaración de unipersonalidad',
                  'Pérdida del caracter de unipersonalidad', 'Reapertura hoja registral',
                  'Adaptación Ley 2/95',
                  'Cierre provisional hoja registral por baja en el índice de Entidades Jurídicas',
                  'Cierre provisional de la hoja registral por revocación del NIF',
                  'Reactivación de la sociedad (Art. 242 del Reglamento del Registro Mercantil)']

# Palabras clave seguidas por :
COLON_KEYWORDS = ['Cambio de identidad del socio único', 'Fe de erratas', 'Socio único']

# Palabra clave
ENDING_KEYWORD = ['Datos registrales']

ALL_KEYWORDS = ARG_KEYWORDS + NOARG_KEYWORDS + COLON_KEYWORDS + ENDING_KEYWORD

DICT_KEYWORDS = {kw: remove_accents(kw).replace(' del ', ' ').replace(' por ', ' ').replace(' de ', ' ')
                 .replace(' ', '_').replace('/', '_').replace('.', '_').lower() for kw in ALL_KEYWORDS}
"""
>>> DICT_KEYWORDS.values()
[u'revocaciones', u'cambio_objeto_social', u'reelecciones', u'otros_conceptos', u'fe_erratas', u'sociedad_unipersonal', u'declaracion_unipersonalidad', u'constitucion', u'suspension_pagos', u'
perdida_caracter_unipersonalidad', u'cancelaciones_oficio_nombramientos', u'datos_registrales', u'cambio_domicilio_social', u'disolucion', u'ampliacion_objeto_social', u'cierre_provisional_hoj
a_registral_baja_en_el_indice_entidades_juridicas', u'ceses_dimisiones', u'nombramientos', u'situacion_concursal', u'modificaciones_estatutarias', u'ampliacion_capital', u'adaptacion_ley_2_95'
, u'cambio_denominacion_social', u'extincion', u'reduccion_capital', u'cambio_identidad_socio_unico', u'transformacion_sociedad', u'reapertura_hoja_registral', u'socio_unico', u'articulo_378_5
_reglamento_registro_mercantil', u'fusion_absorcion']
"""

CARGOS_KEYWORD = ['Consejero', 'Presidente', 'Vicepresid', 'Secretario', 'Cons.Del.Man', 'Adm. Unico',
                  'Mie.Cons.Rec', 'Pre.Cons.Rec', 'Sec.Cons.Rec', 'Adm. Solid.', 'Apoderado', 'Soc.Prof',
                  'Apo.Man.Soli', 'Apo.Manc', 'Apo.Sol', 'Vicesecret', 'Adm. Mancom', 'Co.De.Ma.So',
                  'Cons.Del.Sol', 'Representan', 'Con.Delegado', 'APOD.SOL/MAN', 'LiquiSoli', 'Liquidador',
                  'APODERAD.SOL', 'REPR.143 RRM', 'CONS. DELEG.', 'Aud.C.Con.', 'SecreNoConsj', 'LiqSolid',
                  'CONSEJERO', 'CONS.DEL.M/S', 'VsecrNoConsj', 'Auditor', 'ADM.CONCURS', 'REP.ADM.CONC',
                  'Aud.Supl']

CSV_HEADERS = ['ID', 'Nombre']
CSV_HEADERS.extend(NOARG_KEYWORDS)
CSV_HEADERS.extend(COLON_KEYWORDS)
CSV_HEADERS.extend(ARG_KEYWORDS)
CSV_HEADERS.extend(ENDING_KEYWORD)


# Simplemente implementa parse_line
class LBCommonParser():
    LOGFILE = 'bormeplain.log'
    DEFAULT_OUT_DIR = 'plain'
    REWRITE = False  # Allows resuming
    NAME = '2'

    def __init__(self, _level=logging.INFO):
        # Logs warnings, errors and criticals to stdout and file
        logging.basicConfig(filename=self.LOGFILE, level=_level, format='%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
        self.logger = logging.getLogger("plainBORME")  # name

        h1 = logging.StreamHandler(sys.stdout)
        h1.setLevel(_level)
        self.logger.addHandler(h1)

        self.results = {'error': 0, 'skip': 0, 'ok': 0, 'warning': 0}
        self.data = {}

    def parse_line(self, filename_in, filename_out):
        raise NotImplementedError

    def parse_file(self, filenameIn, filenameOut):
        """
            Parse file according to BORME PDF format

            filename:
            filenameOut:
        """

        had_warning = False

        if os.path.isdir(filenameOut):
            filenameOut = os.path.join(filenameOut, os.path.basename(filenameIn))

        if os.path.exists(filenameOut) and not self.REWRITE:
            self.logger.info('Skipping file %s already exists and rewriting is disabled!' % filenameOut)
            return False

        fp = open(filenameIn, 'r')
        text = fp.read()
        fp.close()

        outfp = open(filenameOut, 'w')
        self.print_header(outfp)

        for trozo in text.split('.\n\n'):
            self.data = {}
            trozo += '.'

            try:
                self.parse_line(trozo)
                self.logger.debug('###########')
                self.print_line(outfp)
                self.logger.debug('###########')
            except Exception, e:
                self.logger.error(e)
                had_warning = True
                self.logger.warning('###########')
                self.logger.warning('SKIPPING. Invalid data found:')
                self.logger.warning(trozo)
                self.logger.warning('###########')
                self.results['warning'] += 1

        self.print_footer(outfp)
        outfp.close()

        if had_warning:
            self.results['error'] += 1

        return True

    def get_filename_out(self, basename):
        filename_out = "%s.%s.plain" % (basename, self.NAME)
        return filename_out

    def parse_dir(self, dirIn, dirOut):
        """
            Parse files in batch mode

            dirIn:
            dirOut:
        """
        _, _, files = os.walk(dirIn).next()
        total = len(files)

        for i, f in enumerate(files):
            filename_out = self.get_filename_out(f)
            filename_out = os.path.join(dirOut, filename_out)

            self.logger.info("[%d/%d] Writing %s", i + 1, total, filename_out)
            filename = os.path.join(dirIn, f)
            try:
                res = self.parse_file(filename, filename_out)
                if res:
                    self.logger.info("OK")
                    self.results['ok'] += 1
                else:
                    self.logger.info("SKIP")
                    self.results['skip'] += 1
            except:
                self.logger.info("ERROR")
                self.logger.exception("Error processing file %s", filename)
                self.results['error'] += 1

    def save_field(self, content):
        self.logger.debug('Guardando %s', content)

        self.data[content[0]] = content[1]

        if not 'total' in self.data:
            self.data['total'] = 1
        else:
            self.data['total'] += 1

    def print_header(self, outfp):
        line = ""
        for k in CSV_HEADERS:
            line += k + '\n'
        line += '----------------------------------------------------------\n'
        self.logger.debug(line)
        outfp.write(line)

    def print_line(self, outfp):
        self.logger.debug('Keys: %s total: %d', self.data.keys(), self.data['total'])
        self.logger.debug('%s', self.data)
        line = ""

        for k in CSV_HEADERS:
            if k in self.data:
                line += self.data[k]
            line += '\n'
        line += '----------------------------------------------------------\n'
        self.logger.debug(line)
        outfp.write(line)

    def print_footer(self, outfp):
        pass

    def show_stats(self):
        elapsed_time = time.time() - self.start_time
        self.logger.info('\nElapsed time: %.2f seconds' % elapsed_time)
        self.logger.info('Results:')
        self.logger.info('  Parsed: %d' % self.results['ok'])
        self.logger.info('  Warning: %d' % self.results['warning'])
        self.logger.info('  Skipped: %d' % self.results['skip'])

        if self.results['error'] > 0:
            self.logger.info('  Errors: %d (see %s for more information).' % (self.results['error'], self.LOGFILE))
        else:
            self.logger.info('  Errors: %d' % self.results['error'])

    def main(self, argv):
        self.start_time = time.time()

        filenameIn = argv[1]
        if os.path.isdir(filenameIn):
            filenameOut = argv[2] if len(argv) > 2 else self.DEFAULT_OUT_DIR
            if os.path.isdir(filenameOut):
                self.parse_dir(filenameIn, filenameOut)
            else:
                if filenameOut == self.DEFAULT_OUT_DIR:
                    os.mkdir(self.DEFAULT_OUT_DIR)
                    self.parse_dir(filenameIn, filenameOut)
                else:
                    self.logger.exception("If first parameter is a directory, second one must be too and exist")
                    sys.exit(1)

        elif os.path.isfile(filenameIn):

            filenameOut = argv[2] if len(argv) > 2 else self.get_filename_out(os.path.basename(filenameIn))
            filenameOut = os.path.join(self.DEFAULT_OUT_DIR, filenameOut)
            self.logger.info('[1/1] Writing %s' % filenameOut)
            try:
                res = self.parse_file(filenameIn, filenameOut)
                if res:
                    self.logger.info('OK')
                    self.results['ok'] += 1
                else:
                    self.logger.info('SKIP')
                    self.results['skip'] += 1
            except:
                self.logger.info('ERROR')
                self.logger.exception("Error processing file %s", filenameIn)
                self.results['error'] += 1
        else:
            self.logger.error("File %s doesn't exist" % filenameIn)


class CSVLBCommonParser(LBCommonParser):
    LOGFILE = 'bormecsv.log'
    DEFAULT_OUT_DIR = 'csv'

    def get_filename_out(self, basename):
        filename_out = "%s.%s.csv" % (basename, self.NAME)
        return filename_out

    def print_header(self, outfp):
        line = ""
        for k in CSV_HEADERS:
            line += '"' + k + '",'
        line = line[:-1] + '\n'
        self.logger.debug(line)
        outfp.write(line)

    def print_line(self, outfp):
        self.logger.debug('Keys: %s total: %d', self.data.keys(), self.data['total'])
        self.logger.debug('%s', self.data)
        line = ""

        # print CSV-friendly
        for k in CSV_HEADERS:
            if k in self.data:
                content = '"' + self.data[k].replace('"', '\\"') + '"'
                line += content
            line += ','
        line = line[:-1] + '\n'

        self.logger.debug(line)
        outfp.write(line)


class JSONLBCommonParser(LBCommonParser):

    LOGFILE = 'bormejson.log'
    DEFAULT_OUT_DIR = 'json'

    jsondata = []

    def get_filename_out(self, basename):
        return "%s.%s.json" % (basename, self.NAME)

    def print_header(self, outfp):
        pass

    def print_footer(self, outfp):
        outfp.write(json.dumps(self.jsondata, sort_keys=True, indent=4))
        #outfp.write(json.dumps(self.jsondata))

    def print_line(self, outfp):
        self.logger.debug('Keys: %s total: %d', self.data.keys(), self.data['total'])
        self.logger.debug('%s', self.data)
        del self.data['total']
        self.jsondata.append(self.data)


class BSONLBCommonParser(LBCommonParser):

    LOGFILE = 'bormebson.log'
    DEFAULT_OUT_DIR = 'bson'

    def get_filename_out(self, basename):
        return "%s.%s.bson" % (basename, self.NAME)

    def print_header(self, outfp):
        pass

    def print_line(self, outfp):
        self.logger.debug('Keys: %s total: %d', self.data.keys(), self.data['total'])
        self.logger.debug('%s', self.data)
        del self.data['total']
        outfp.write(BSON.encode(self.data))


def get_borme_filename_xml(day):
    return "BORME-S-" + day.strftime('%Y%m%d') + ".xml"


def get_borme_xml_url(day):
    return BORME_XML_URL + day.strftime('%Y%m%d')


def download_url(url, filename):
    if os.path.exists(filename):
        return False

    r = requests.get(url, stream=True)
    cl = r.headers.get('content-length')
    print "%.2f KB" % (int(cl) / 1024.0)

    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(8192):
            fd.write(chunk)

    return True

# https
URL_BASE = 'http://www.boe.es'
