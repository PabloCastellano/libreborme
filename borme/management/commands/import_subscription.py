from django.core.management.base import BaseCommand

import logging
import time

import alertas.importer


class Command(BaseCommand):
    help = 'Import BORME JSON file(s)'

    def add_arguments(self, parser):
        parser.add_argument('files', metavar='FILE', nargs='+', type=str)

    def handle(self, *args, **options):
        self.set_verbosity(int(options['verbosity']))
        start_time = time.time()

        for filename in options["files"]:
            print(filename)
            alertas.importer.import_subscription_event(filename)

        # Elapsed time
        elapsed_time = time.time() - start_time
        print('\nElapsed time: %.2f seconds' % elapsed_time)

    def set_verbosity(self, verbosity):
        if verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)
