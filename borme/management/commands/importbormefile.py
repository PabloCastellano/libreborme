# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from borme.models import Config

import time
from datetime import datetime
from libreborme.utils import get_git_revision_short_hash
from borme.utils import import_borme_file


class Command(BaseCommand):
    args = '<BORME files, ...>'
    help = 'Import BORME file'

    def handle(self, *args, **options):
        start_time = time.time()

        if args:
            for filename in args:
                print(filename)
                import_borme_file(filename)

            config = Config.objects.first()
            if config:
                config.last_modified = datetime.today()
            else:
                config = Config(last_modified=datetime.today())
            config.version = get_git_revision_short_hash()
            config.save()

        # Elapsed time
        elapsed_time = time.time() - start_time
        print('\nElapsed time: %.2f seconds' % elapsed_time)
