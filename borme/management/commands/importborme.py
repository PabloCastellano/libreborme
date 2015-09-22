# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from borme.models import Config

import time
import datetime
from libreborme.utils import get_git_revision_short_hash
from borme.utils import import_borme_download


class Command(BaseCommand):
    args = '<ISO formmated date (ex. 2015-01-01)> [--local]'
    help = 'Import BORMEs from date'

    def handle(self, *args, **options):
        start_time = time.time()

        if args:
            local = len(args) > 1 and args[1] == 'local'
            date = datetime.date(*map(int, args[0].split('-')))
            import_borme_download(date, download=not local)

            config = Config.objects.first()
            if config:
                config.last_modified = datetime.datetime.today()
            else:
                config = Config(last_modified=datetime.datetime.today())
            config.version = get_git_revision_short_hash()
            config.save()

            # Elapsed time
            elapsed_time = time.time() - start_time
            print('\nElapsed time: %.2f seconds' % elapsed_time)
