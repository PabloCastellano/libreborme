# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from borme.models import Config

import time
import logging

from libreborme.utils import get_git_revision_short_hash
from borme.importer import import_borme_json
import borme.importer


class Command(BaseCommand):
    args = '<BORME files, ...>'
    help = 'Import BORME JSON file'

    def add_arguments(self, parser):
        parser.add_argument('filename', help='BORME-JSON filename')
        parser.add_argument('-s', '--stats', action='store_true', default=False, help='Save stats log file')

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])
        if verbosity == 0:
            borme.importer.logger.setLevel(logging.ERROR)
        elif verbosity == 1:  # default
            borme.importer.logger.setLevel(logging.INFO)
        elif verbosity == 2:
            borme.importer.logger.setLevel(logging.INFO)
        elif verbosity > 2:
            borme.importer.logger.setLevel(logging.DEBUG)
        if verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)
        start_time = time.time()

        print(options['filename'])
        import_borme_json(options['filename'], save_stats=options['stats'])

        # Elapsed time
        elapsed_time = time.time() - start_time
        print('\nElapsed time: %.2f seconds' % elapsed_time)
