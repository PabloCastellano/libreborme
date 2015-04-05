#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import logging
import getopt

from borme_parser import *

# OR de las palabras clave con argumentos
RE_ARG_KEYWORDS = '(%s)' % '|'.join(ARG_KEYWORDS)
# OR de todas las palabras clave, "non grouping"
RE_ALL_KEYWORDS_NG = '(?:%s|%s|%s|%s)' % ('|'.join(ARG_KEYWORDS), '|'.join(COLON_KEYWORDS), '|'.join(NOARG_KEYWORDS), ENDING_KEYWORD[0])
# OR de las palabras clave sin argumentos
RE_NOARG_KEYWORDS = '(%s)' % '|'.join(NOARG_KEYWORDS)
# OR de las palabras clave con argumentos seguidas por :
RE_COLON_KEYWORDS = '(%s)' % '|'.join(COLON_KEYWORDS)
RE_ENDING_KEYWORD = '(%s)' % ENDING_KEYWORD[0]

# Cargos
"""
RE_CARGOS_KEYWORD = '(%s)' % '|'.join(CARGOS_KEYWORD)
RE_CARGOS_KEYWORD_NG = '(?:\.\s*%s|$)' % '|'.join(RE_CARGOS_KEYWORD) # MAL, FIX, pero funciona RE_...
for match in re.finditer(RE_CARGOS_KEYWORD + ':\s+(.*?)' + RE_CARGOS_KEYWORD_NG, str1):
    print match.group(1), match.group(2)
"""

class CSV4LBCommonParser(LBCommonParser):

    LOGFILE = 'bormecsv.log'
    DEFAULT_OUT_DIR = 'csv'
    REWRITE = True  # Allows resuming
    CSV = False
    NAME = '4c'

    # TODO: Compilar las regexp para mayor eficiencia
    # http://stackoverflow.com/questions/16720541/python-string-replace-regular-expression
    # regexp = re.compile(...)
    # m = regexp.findal(...)
    def parse_line(self, trozo):

        tr2_ = trozo.replace('\n', ' ').replace('  ', ' ')
        self.logger.debug(tr2_)

        m = re.match('^(\d+) - (.*?)\.\s*' + RE_ALL_KEYWORDS_NG, tr2_)

        self.save_field(('ID', m.group(1)))
        self.save_field(('Nombre', m.group(2)))

        for match in re.finditer('(?=' + RE_ARG_KEYWORDS + '\.\s+(.*?)\.\s*' + RE_ALL_KEYWORDS_NG + ')', tr2_):
            self.save_field((match.group(1), match.group(2)))

        for match in re.finditer(RE_COLON_KEYWORDS + ':\s+(.*?)\.\s*' + RE_ALL_KEYWORDS_NG, tr2_):
            self.save_field((match.group(1), match.group(2)))

        for match in re.finditer(RE_ENDING_KEYWORD + '\.\s+(.*)\.\s*', tr2_):
            self.save_field((match.group(1), match.group(2)))

        for match in re.finditer(RE_NOARG_KEYWORDS + '\.', tr2_):
            self.save_field((match.group(1), 'X'))


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

    #parser = CSV4LBCommonParser(logging.DEBUG)
    parser = CSV4LBCommonParser(logging_level, csv_format)
    parser.main(sys.argv)
    parser.show_stats()
