# PRIVATE
from django.core.management.base import BaseCommand
from django.utils import timezone

from datetime import datetime
import logging
import time

from borme.models import Company
import libreborme.nif

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # args = '<ISO formatted date (ex. 2015-01-01 or --init)> [--local]'
    help = 'Find NIF for companies that have been modified some day'

    def add_arguments(self, parser):
        parser.add_argument(
                '--today',
                action='store_true',
                required=False,
                help='Find NIF for companies modified today')
        parser.add_argument(
                '-d', '--date',
                type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                required=False,
                help='Find NIF for companies modified this day (YYYY-mm-dd)')

    def handle(self, *args, **options):
        self.set_verbosity(int(options['verbosity']))

        if options['today']:
            companies = Company.objects.get_modified_today()
        elif options['date']:
            companies = Company.objects.get_modified_on(options['date'])

        total = len(companies)
        logger.info("Found {} companies".format(total))
        if total == 0:
            return

        logger.debug(companies)

        found = 0
        added = 0
        skipped = 0
        for num, company in enumerate(companies, 1):
            # mejorar, tenemos el tipo y podemos generar otro slug
            # necesitamos busqueda si o si
            try:
                nif, created, provider = libreborme.nif.find_nif(company.slug)
                if created:
                    added += 1
                else:
                    skipped += 1
                if nif:
                    found += 1

            except libreborme.nif.NIFNotFoundException:
                print("[{}/{}] {}: ERROR (not found)".format(num, total, company.slug))
            except libreborme.nif.NIFParserException:
                print("[{}/{}] {}: ERROR (parsing)".format(num, total, company.slug))
            except libreborme.nif.NIFInvalidException as e:
                print("[{}/{}] {}: ERROR (invalid): '{}'".format(num, total, company.slug, e))
            else:
                if created:
                    print("[{}/{}] {}: NEW [{}] ({})".format(num, total, company.slug, nif, provider))
                else:
                    print("[{}/{}] {}: SKIP [{}]".format(num, total, company.slug, nif))
            time.sleep(1)

        logger.info("Result: found NIF for {} out of {} companies. NEW: {}, SKIPPED: {}".format(found, total, added, skipped))

    def set_verbosity(self, verbosity):
        if verbosity == 0:
            logging.getLogger('nif').setLevel(logging.ERROR)
        elif verbosity == 1:  # default
            logging.getLogger('nif').setLevel(logging.INFO)
        elif verbosity == 2:
            logging.getLogger('nif').setLevel(logging.INFO)
        elif verbosity > 2:
            logging.getLogger('nif').setLevel(logging.DEBUG)
