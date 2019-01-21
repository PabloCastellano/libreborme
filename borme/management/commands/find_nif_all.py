# PRIVATE
from django.core.management.base import BaseCommand

import logging
import time

from borme.models import Company
import libreborme.nif

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # args = '<ISO formatted date (ex. 2015-01-01 or --init)> [--local]'
    help = 'Find NIF for a Company'

    def handle(self, *args, **options):
        self.set_verbosity(int(options['verbosity']))

        companies = Company.objects.filter(nif__isnull=True).order_by('name')

        total = len(companies)
        print("Found {} companies".format(total))
        if total == 0:
            return

        print("Will start in 5 seconds")
        time.sleep(5)

        found = 0
        added = 0
        for num, company in enumerate(companies, 1):
            try:
                nif, created, provider = libreborme.nif.find_nif(company)
                if created:
                    added += 1
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

        notfound = total - found
        skipped = total - added
        print("Result: found NIF for {} out of {} companies. NEW: {}, SKIPPED: {} NOTFOUND: {}".format(found, total, added, skipped, notfound))

    def set_verbosity(self, verbosity):
        if verbosity == 0:
            logging.getLogger('libreborme.nif').setLevel(logging.ERROR)
        elif verbosity == 1:  # default
            logging.getLogger('libreborme.nif').setLevel(logging.INFO)
        elif verbosity == 2:
            logging.getLogger('libreborme.nif').setLevel(logging.INFO)
        elif verbosity > 2:
            logging.getLogger('libreborme.nif').setLevel(logging.DEBUG)
