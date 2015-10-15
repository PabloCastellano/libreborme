# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.utils import timezone

from borme.models import Config

from libreborme.utils import get_git_revision_short_hash


class Command(BaseCommand):
    help = 'Update current Git version hash'

    def handle(self, *args, **options):
        config = Config.objects.first()
        version = get_git_revision_short_hash()
        print(version)
        if config:
            config.version = version
        else:
            date = timezone.make_aware(timezone.datetime(2000, 1, 1))
            config = Config(version=version, last_modified=date)
        config.save()
