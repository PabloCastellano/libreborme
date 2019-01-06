# PRIVATE
from django.core.management.base import BaseCommand
from django.utils import timezone

import logging

from libreborme.nif import find_nif, PROVIDERS

class Command(BaseCommand):
    # args = '<ISO formatted date (ex. 2015-01-01 or --init)> [--local]'
    help = 'Find NIF for a Company'

    def add_arguments(self, parser):
        parser.add_argument('company', nargs='+', type=str,
                            help="Company name or slug")
        parser.add_argument(
                '-p', '--provider',
                required=False,
                choices=PROVIDERS,
                help='Provider to retrieve NIF from')
        parser.add_argument(
                '-s', '--save',
                action="store_false",
                required=False,
                default=True,
                help='Save to DB (default: True)')

    def handle(self, *args, **options):
        self.set_verbosity(int(options['verbosity']))

        for company in options['company']:
            nif = find_nif(company, provider=options['provider'], save_to_db=options['save'])
            if nif:
                print(nif)
            else:
                print("Not found")

    def set_verbosity(self, verbosity):
        if verbosity == 0:
            logging.getLogger('libreborme.nif').setLevel(logging.ERROR)
        elif verbosity == 1:  # default
            logging.getLogger('libreborme.nif').setLevel(logging.INFO)
        elif verbosity == 2:
            logging.getLogger('libreborme.nif').setLevel(logging.INFO)
        elif verbosity > 2:
            logging.getLogger('libreborme.nif').setLevel(logging.DEBUG)
