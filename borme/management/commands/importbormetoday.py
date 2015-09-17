# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from borme.models import Config

import time
import datetime
from libreborme.utils import get_git_revision_short_hash
from borme.utils import import_borme_download


class Command(BaseCommand):
    args = '[--local]'
    help = 'Import BORMEs from today'

    def handle(self, *args, **options):
        start_time = time.time()

        local = args and args[0] == 'local'
        date = datetime.date.today()
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
