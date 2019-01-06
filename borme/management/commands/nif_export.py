# PRIVATE
from django.core.management.base import BaseCommand

import logging

import libreborme.nif

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # args = '<ISO formatted date (ex. 2015-01-01 or --init)> [--local]'
    help = 'Export Company NIFs'

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument(
                '-f', '--format',
                required=False,
                help='Output format (default: csv) [FUTURE]')

    def handle(self, *args, **options):
        total = libreborme.nif.export(options['filename'])
        logger.info("Exported {} companies to {}".format(total, options['filename']))
