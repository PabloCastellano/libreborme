#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import logging

from common import *

# OR de las palabras clave con argumentos
RE_ARG_KEYWORDS = '(%s)' % '|'.join(ARG_KEYWORDS)
# OR de todas las palabras clave, "non grouping"
RE_ALL_KEYWORDS_NG = '(?:%s|%s|%s|%s)' % ('|'.join(ARG_KEYWORDS), '|'.join(COLON_KEYWORDS), '|'.join(NOARG_KEYWORDS), ENDING_KEYWORD[0])
# OR de las palabras clave sin argumentos
RE_NOARG_KEYWORDS = '(%s)' % '|'.join(NOARG_KEYWORDS)
# OR de las palabras clave con argumentos seguidas por :
RE_COLON_KEYWORDS = '(%s)' % '|'.join(COLON_KEYWORDS)
RE_ENDING_KEYWORD = '(%s)' % ENDING_KEYWORD[0]


class CSV4LBCommonParser(LBCommonParser):

    LOGFILE = 'bormecsv.log'
    DEFAULT_OUT_DIR = 'csv'
    REWRITE = True  # Allows resuming
    CSV = False
    NAME = '4c'

    def parse_line(self, trozo):

        tr2_ = trozo.replace('\n', ' ').replace('  ', ' ')
        self.logger.debug(tr2_)

        m = re.match('^(\d+) - (.*)\.\s*' + RE_ALL_KEYWORDS_NG, tr2_)

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


if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(-1)

    #parser = CSV4LBCommonParser(logging.DEBUG)
    parser = CSV4LBCommonParser()
    parser.main(sys.argv)
    parser.show_stats()
