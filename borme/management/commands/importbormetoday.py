from django.core.management.base import BaseCommand
from django.utils import timezone

from borme.importer import psql_update_documents
from borme.models import Config

import datetime
import time

from borme.importer import import_borme_download, update_previous_xml


class Command(BaseCommand):
    help = 'Import BORMEs from today'

    def add_arguments(self, parser):
        parser.add_argument('--local-only',
                            action='store_true',
                            default=False,
                            help='Do not download any file')

    def handle(self, *args, **options):
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
