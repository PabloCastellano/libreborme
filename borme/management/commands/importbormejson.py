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

        if args:
            for filename in args:
                print(filename)
                import_borme_json(filename)

            config = Config.objects.first()
            if config:
                config.last_modified = timezone.now()
            else:
                config = Config(last_modified=timezone.now())
            config.version = get_git_revision_short_hash()
            config.save()

        # Elapsed time
        elapsed_time = time.time() - start_time
        print('\nElapsed time: %.2f seconds' % elapsed_time)
