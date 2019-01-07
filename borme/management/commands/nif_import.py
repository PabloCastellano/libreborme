# PRIVATE
from django.core.management.base import BaseCommand

import logging

import libreborme.nif

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    # args = '<ISO formatted date (ex. 2015-01-01 or --init)> [--local]'
    help = 'Import Company NIFs'

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument(
                '-f', '--format',
                required=False,
                help='Output format (default: csv) [FUTURE]')

    def handle(self, *args, **options):
        logging.getLogger('nif').setLevel(logging.DEBUG)
        added, skipped, error = libreborme.nif.import_csv(options['filename'])
        logger.info("Imported NIF for {} companies ({} skipped, {} errored)".format(added, skipped, error))
