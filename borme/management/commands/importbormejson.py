from django.core.management.base import BaseCommand
from django.utils import timezone
from borme.models import Config

import time
import logging

from libreborme.utils import get_git_revision_short_hash
from borme.importer import import_borme_json
import borme.importer


class Command(BaseCommand):
    help = 'Import BORME JSON file(s)'

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

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
            logging.getLogger().setLevel(logging.DEBUG)
        start_time = time.time()

        for filename in options["files"]:
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
