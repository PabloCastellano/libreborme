# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from borme.models import Config

import datetime
import time

from borme.importer import import_borme_download, update_previous_xml


class Command(BaseCommand):
    args = '[--local]'
    help = 'Import BORMEs from today'

    def handle(self, *args, **options):
        start_time = time.time()

        local = args and args[0] == 'local'
        date = datetime.date.today()
        success = import_borme_download(date.strftime('%Y-%m-%d'), download=not local)
        if success:
            update_previous_xml(date)

            config = Config.objects.first()
            if config:
                config.last_modified = timezone.now()
            else:
                config = Config(last_modified=timezone.now())
            config.save()

        # Elapsed time
        elapsed_time = time.time() - start_time
        print('\nElapsed time: %.2f seconds' % elapsed_time)
