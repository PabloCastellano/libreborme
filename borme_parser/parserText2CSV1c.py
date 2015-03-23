#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

from borme_parser import LBCommonParser

class CSV1LBCommonParser(LBCommonParser):

    LOGFILE = 'bormecsv.log'
    DEFAULT_OUT_DIR = 'csv'
    REWRITE = True  # Allows resuming
    CSV = False
    NAME = '1c'

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

        m = re.findall('(Reelecciones|Declaración de unipersonalidad|Nombramientos|Revocaciones|Ceses/Dimisiones|Constitución)\.\s+(.*?):\s+(.*?)\.', tr2_)

        #BORME-A-2014-88-25.pdf
        # Disolución. Voluntaria.

        if m != []:
            for algo in m:
                #print algo
                self.save_field(algo)

        m = re.findall('(Datos registrales)\.\s+(.*)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                self.save_field(algo)

        # FIXME: Determinar cuándo acaba el texto (con puntos en medio) de las modificaciones estatutarias.
        m = re.findall('(Modificaciones estatutarias)\.\s+(.*?)\.\s*(?:Datos registrales|Cambio de objeto social)', tr2_)
        if m != []:
            for algo in m:
                #print algo
                self.save_field(algo)

        m = re.findall('(Cambio de denominación social|Cambio de domicilio social|Ampliacion del objeto social)\.\s+(.*?)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                self.save_field(algo)

        m = re.findall('(Cambio de identidad del socio único|TEST):\s+(.*?)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                self.save_field(algo)

        m = re.findall('(Sociedad unipersonal|Extinción)\.\s*', tr2_)
        if m != []:
            for algo in m:
                #print algo
                self.save_field((algo, 'X'))



if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(-1)

    parser = CSV1LBCommonParser()
    parser.main(sys.argv)
    parser.show_stats()
