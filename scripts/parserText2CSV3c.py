#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import logging

from common import LBCommonParser

ALL_KEYWORDS = ['Reelecciones', 'Declaración de unipersonalidad', 'Nombramientos', 'Revocaciones', 'Ceses/Dimisiones',
                'Constitución', 'Datos registrales', 'Modificaciones estatutarias', 'Cambio de objeto social',
                'Cambio de denominación social', 'Cambio de domicilio social', 'Ampliacion del objeto social',
                'Cambio de identidad del socio único', 'Sociedad unipersonal', 'Extinción']
RE_OR_KEYWORDS = '(' + '|'.join(ALL_KEYWORDS) + ')'
RE_NOR_KEYWORDS = '(?:' + '|'.join(ALL_KEYWORDS) + ')'

class CSV3LBCommonParser(LBCommonParser):

    LOGFILE = 'bormecsv.log'
    DEFAULT_OUT_DIR = 'csv'
    REWRITE = True  # Allows resuming
    CSV = False
    NAME = '3c'

    def parse_line(self, trozo):

        # ['Modificaciones estatutarias.  Modificaci\xc3\xb3n del art. 27\xc2\xba de los estatutos en orden a la retribuci\xc3\xb3n del \xc3\xb3rgano de administraci\xc3\xb3n.- .', 'Datos registrales. T 2579 , F 215, S 8, H PM 74389, I/A 2 (22.01.15)']
        tr2 = trozo.split('\n')[1:]
        #tr2_ = ''.join(tr2)

        # Modificaciones estatutarias.  Modificación del art. 27º de los estatutos en orden a la retribución del órgano de administración.- . Datos registrales. T 2579 , F 215, S 8, H PM 74389, I/A 2 (22.01.15)
        tr2_ = ' '.join(tr2)

        self.logger.debug(trozo)
        self.logger.debug(tr2_)

        m = re.match('(\d+) - (.*)\.\n', trozo)

        self.save_field(('ID', m.group(1)))
        self.save_field(('Nombre', m.group(2)))

        #m = re.findall('(Reelecciones|Declaración de unipersonalidad|Nombramientos|Revocaciones|Ceses/Dimisiones|Constitución)\.\s+(.*?):\s+(.*?)\.', tr2_)
        m = re.findall(RE_OR_KEYWORDS + '\.\s+(.*)\.\s*' + RE_NOR_KEYWORDS, tr2_)

        #BORME-A-2014-88-25.pdf
        # Disolución. Voluntaria.

        if m != []:
            for algo in m:
                #print algo
                self.save_field(algo)

        m = re.findall('(Sociedad unipersonal|Extinción)\.', tr2_)
        if m != []:
            for algo in m:
                #print algo
                self.save_field((algo, 'X'))


if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(-1)

    parser = CSV3LBCommonParser(logging.DEBUG)
    #parser = CSV3LBCommonParser()
    parser.main(sys.argv)
    parser.show_stats()
