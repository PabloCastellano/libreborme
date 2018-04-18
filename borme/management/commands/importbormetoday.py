from django.core.management.base import BaseCommand
from django.utils import timezone

import datetime
import logging
import time

from borme.models import Config
from borme.parser.importer import import_borme_download
from borme.parser.path import update_previous_xml
from borme.parser.postgres import psql_update_documents
import borme.parser.importer


class Command(BaseCommand):
    help = 'Import BORMEs from today'

    def add_arguments(self, parser):
        parser.add_argument('--local-only',
                            action='store_true',
                            default=False,
                            help='Do not download any file')

    def handle(self, *args, **options):
        self.set_verbosity(int(options['verbosity']))
        start_time = time.time()

        date = datetime.date.today()
        datestr = date.strftime('%Y-%m-%d')
        success = import_borme_download(datestr,
                                        datestr,
                                        local_only=options['local_only'])

        if success:
            update_previous_xml(date)

            config = Config.objects.first()
            if config:
                config.last_modified = timezone.now()
            else:
                config = Config(last_modified=timezone.now())
            config.save()

        # Update Full Text Search
        psql_update_documents()

        # Elapsed time
        elapsed_time = time.time() - start_time
        print('\nElapsed time: %.2f seconds' % elapsed_time)

    def set_verbosity(self, verbosity):
        if verbosity == 0:
            borme.parser.importer.logger.setLevel(logging.ERROR)
        elif verbosity == 1:  # default
            borme.parser.importer.logger.setLevel(logging.INFO)
        elif verbosity == 2:
            borme.parser.importer.logger.setLevel(logging.INFO)
        elif verbosity > 2:
            borme.parser.importer.logger.setLevel(logging.DEBUG)
            logging.getLogger().setLevel(logging.DEBUG)
