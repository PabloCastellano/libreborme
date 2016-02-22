#from django.core.management.base import CommandError
from django.core.management.base import BaseCommand
from borme.models import Config

import time
from django.conf import settings
from django.utils import timezone
from libreborme.utils import get_git_revision_short_hash
from borme.importer import import_borme_download


class Command(BaseCommand):
    #args = '<ISO formatted date (ex. 2015-01-01 or --init)> [--local]'
    help = 'Import BORMEs from date'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--from', nargs=1, required=True, help='ISO formatted date (ex. 2015-01-01) or "init"')
        parser.add_argument('-t', '--to', nargs=1, required=True, help='ISO formatted date (ex. 2016-01-01) or "today"')
        parser.add_argument('--local-only', action='store_true', default=False, help='Do not download any file')
        parser.add_argument('--no-missing', action='store_true', default=False, help='Abort if local file is not found')
        # json only, pdf only...

    def handle(self, *args, **options):
        start_time = time.time()

        if settings.DEBUG:
            print('WARNING: DEBUG is ON and so Django will save every query executed.')
            print('It will result in this command using more and more memory specially when you import several months of BORME.')
            print('Process will start in 5 seconds.\n')
            time.sleep(5)

        import_borme_download(options['from'][0], options['to'][0], local_only=options['local_only'], no_missing=options['no_missing'])

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
