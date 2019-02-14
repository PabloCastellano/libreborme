from django.core.management.base import BaseCommand

import json
import logging
import time
import os.path
import sys

import alertas.importer
import alertas.parser

logger = logging.getLogger(__name__)


# TODO: en vez de por filename por fecha de borme (y provincia)
class Command(BaseCommand):
    help = 'Generate Subscription JSON from BORME-JSON file(s)'

    def add_arguments(self, parser):
        parser.add_argument('event')
        parser.add_argument('files', metavar='FILE', nargs='+')
        parser.add_argument('--import', action="store_true",
                            help="Generate and Import at the same time")
        parser.add_argument('-o', '--output',
                            help="Output dir OR 'stdout'")

    def handle(self, *args, **options):
        self.set_verbosity(int(options['verbosity']))
        start_time = time.time()
        event = options["event"]

        for filepath in options["files"]:
            results = alertas.parser.parse_borme_json(event, filepath)
            if options["output"] == "stdout":
                json.dump(results, sys.stdout, sort_keys=True, indent=4)
            elif options["output"]:
                # From BORME-A-2018-117-03.json to BORME-A-2018-117-03_adm.json
                # TODO: habia algo de ext
                # TODO: output dir de verdad
                filename = os.path.basename(filepath)
                output_filename = os.path.splitext(filename)[0] + "_{}.json".format(event)
                output_filepath = os.path.dirname(filepath) + "/" + output_filename
                print(output_filepath)
                with open(output_filepath, "w") as fp:
                    json.dump(results, fp, sort_keys=True, indent=4)
                logger.info("Written " + output_filepath)

            if options["import"]:
                logger.debug("Importing to DB")
                try:
                    alertas.importer.from_dict(results)
                except ValueError:
                    logger.exception("Parsing file {}".format(filename))

        # Elapsed time
        elapsed_time = time.time() - start_time
        logger.info('Elapsed time: %.2f seconds' % elapsed_time)

    def set_verbosity(self, verbosity):
        pass
        """
        if verbosity == 0:
            borme.parser.importer.logger.setLevel(logging.ERROR)
        elif verbosity == 1:  # default
            borme.parser.importer.logger.setLevel(logging.INFO)
        elif verbosity == 2:
            borme.parser.importer.logger.setLevel(logging.INFO)
        elif verbosity > 2:
            borme.parser.importer.logger.setLevel(logging.DEBUG)
            logging.getLogger().setLevel(logging.DEBUG)
        """
