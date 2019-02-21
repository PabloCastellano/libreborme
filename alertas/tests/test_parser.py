# from borme.models import Anuncio, Borme, BormeLog, Company, Person
from alertas.models import SubscriptionEvent
import alertas.parser
import alertas.importer
import borme.parser.importer
import borme.utils.strings

import datetime
import gzip
import logging
import os

from django.test import TestCase
from django.test.utils import override_settings

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(THIS_PATH, '../../borme/tests/files')

# Disable loggers
borme.parser.importer.logger.setLevel(logging.ERROR)
borme.parser.logger.logger.setLevel(logging.ERROR)
borme.utils.strings.logger.setLevel(logging.ERROR)


@override_settings(PARSER='borme.parser.backend.yabormeparser')
def load_borme_from_gzipped_json(filename):
    fp = gzip.open(os.path.join(FILES_PATH, 'yabormeparser', filename))
    borme.parser.importer.from_json_file(fp, set_url=False)
    return fp


# TODO: Update yabormeaprser gz to latest version 10001
class TestGenSubscription_BORME_A_2012_197_28(TestCase):

    def setUp(self):
        # self.fp_borme1 = gzip.open(os.path.join(FILES_PATH, 'yabormeparser', 'BORME-A-2009-197-28.json.gz'))
        self.fp_borme1 = load_borme_from_gzipped_json('BORME-A-2009-197-28.json.gz')
        self.fp_borme1.seek(0)

    def tearDown(self):
        self.fp_borme1.close()

    def test_import_adm(self):
        # Load BORME
        # borme.parser.importer.from_json_file(self.fp_borme1, set_url=False)
        #
        # Generate subscriptions for day
        results = alertas.parser.parse_borme_json('adm', self.fp_borme1)

        self.assertEqual(results['provincia'], "MADRID")
        self.assertEqual(results['cve'], "BORME-A-2009-197-28")
        self.assertEqual(results['date'], "2009-10-15")

        # Import subscriptions
        alertas.importer.from_dict(results)

        # TODO: check results ?

        subscriptions = SubscriptionEvent.objects.all()
        self.assertEqual(len(subscriptions), 1)

        subscription = subscriptions[0]
        self.assertEqual(subscription.province, "28")
        self.assertEqual(subscription.event, "adm")
        self.assertEqual(subscription.event_date, datetime.date(2009, 10, 15))
        self.assertEqual(len(subscription.data_json), 47)

        for event in subscription.data_json:
            if event["company"]["name"] == "BURGFORD INVESTMENT SL":
                # FIXME: ending dot
                self.assertEqual(event["company"]["address"], "C/ ALFONSO XII - NUMERO 36 3º IZQUIERDA (MADRID).")
                self.assertEqual(event["company"]["nif"], "")
                self.assertEqual(event["company"]["url_api"], "https://api.libreborme.net/v1/empresa/burgford-investment")
                self.assertEqual(event["company"]["url_web"], "https://libreborme.net/borme/empresa/burgford-investment/")
                # FIXME: ending dot
                self.assertEqual(event["datos_registrales"], "T 22861 , F 161, S 8, H M 409334, I/A 6 (30.09.09).")
                self.assertEqual(event["new_roles"], [["ADM. UNICO", "PINILLA RISUEÑO RAUL"]])
            elif event["company"]["name"] == "ARIDOS EXTENDIDOS Y COMPACTACIONES SL":
                self.assertEqual(event["company"]["address"], "")
                self.assertEqual(len(event["new_roles"]), 2)

        # TODO: more checks
