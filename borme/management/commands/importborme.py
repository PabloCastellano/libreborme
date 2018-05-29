from django.core.management.base import BaseCommand
from django.utils import timezone

import logging
import time

from borme.models import Config
from borme.parser.importer import import_borme_download
# from borme.parser.postgres import psql_update_documents
import borme.parser.importer

from libreborme.utils import get_git_revision_short_hash


class Command(BaseCommand):
    # args = '<ISO formatted date (ex. 2015-01-01 or --init)> [--local]'
    help = 'Import BORMEs from date'

    def add_arguments(self, parser):
        parser.add_argument(
                '-f', '--from',
                nargs=1, required=True,
                help='ISO formatted date (ex. 2015-01-01) or "init"')
        parser.add_argument(
                '-t', '--to',
                nargs=1, required=True,
                help='ISO formatted date (ex. 2016-01-01) or "today"')
        parser.add_argument(
                '--local-only',
                action='store_true',
                default=False,
                help='Do not download any file')
        parser.add_argument(
                '--no-missing',
                action='store_true',
                default=False,
                help='Abort if local file is not found')
        # json only, pdf only...

    def handle(self, *args, **options):
        self.set_verbosity(int(options['verbosity']))
        start_time = time.time()

        import_borme_download(options['from'][0],
                              options['to'][0],
                              local_only=options['local_only'],
                              no_missing=options['no_missing'])

        config = Config.objects.first()
        if config:
            config.last_modified = timezone.now()
        else:
            config = Config(last_modified=timezone.now())
        config.version = get_git_revision_short_hash()
        config.save()

        # Update Full Text Search
        # psql_update_documents()

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
