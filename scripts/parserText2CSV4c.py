#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import logging

from common import *

RE_OR_KEYWORDS = '(' + '|'.join(ALL_KEYWORDS) + ')'
RE_NOR_KEYWORDS = '(?:' + '|'.join(ALL_KEYWORDS) + '|' + '|'.join(ALL_KEYWORDS2) + ')'

RE_OR_KEYWORDS2 = '(' + '|'.join(ALL_KEYWORDS2) + ')'

class CSV4LBCommonParser(LBCommonParser):

    LOGFILE = 'bormecsv.log'
    DEFAULT_OUT_DIR = 'csv'
    REWRITE = True  # Allows resuming
    CSV = False
    NAME = '3c'

    def parse_line(self, trozo):

        m = re.match('(\d+) - (.*)\.\n', trozo)

        self.save_field(('ID', m.group(1)))
        self.save_field(('Nombre', m.group(2)))

        tr2 = trozo.split('\n')[1:]
        tr2_ = ' '.join(tr2)
        tr2_ = tr2_.replace('\n', ' ')
        tr2_ = tr2_.replace('  ', ' ')
        self.logger.debug(tr2_)

        # TODO
        """
line = 'bla bla bla<form>Form 1</form> some text...<form>Form 2</form> more text?'
for match in re.finditer('<form>(.*?)</form>', line, re.S):
    print match.group(1)
        """

        m = re.findall('(?=' + RE_OR_KEYWORDS + '\.\s+(.*?)\.\s*' + RE_NOR_KEYWORDS + ')', tr2_)

        if m != []:
            for algo in m:
                self.save_field(algo)

        m = re.findall('(Cambio de identidad del socio único|Fe de erratas|Socio único):\s+(.*?)\.\s*' + RE_NOR_KEYWORDS, tr2_)

        if m != []:
            for algo in m:
                self.save_field(algo)

        m = re.findall('(Datos registrales)\.\s+(.*)\.\s*', tr2_)
        if m != []:
            for algo in m:
                self.save_field(algo)

        m = re.findall(RE_OR_KEYWORDS2 + '\.', tr2_)
        if m != []:
            for algo in m:
                self.save_field((algo, 'X'))


if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(-1)

    parser = CSV4LBCommonParser()
    parser.main(sys.argv)
    parser.show_stats()
