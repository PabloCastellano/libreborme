# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from borme.models import Config

from libreborme.utils import get_git_revision_short_hash


class Command(BaseCommand):
    help = 'Update current Git version hash'

    def handle(self, *args, **options):
        config = Config.objects.first()
        version = get_git_revision_short_hash()
        print version
        if config:
            config.version = version
        else:
            config = Config(version=version)
        config.save()
