from django.contrib.auth import get_user_model
from django.core import mail
from djstripe.models import Subscription

from alertas.models import SubscriptionEvent
import alertas.email
import alertas.importer
import alertas.parser
import alertas.subscriptions
import borme.parser.importer
import borme.utils.strings

import datetime
import gzip
import logging
import os

from django.test import TestCase
from django.test.utils import override_settings

User = get_user_model()

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(THIS_PATH, '../../borme/tests/files')  # FIXME: ugly

# Disable loggers
borme.parser.importer.logger.setLevel(logging.ERROR)
borme.parser.logger.logger.setLevel(logging.ERROR)
borme.utils.strings.logger.setLevel(logging.ERROR)


# TODO: Instead of set_url=False, require xml always
# override_settings(XML_ROOT=...')
@override_settings(PARSER='borme.parser.backend.yabormeparser')
def load_borme_from_gzipped_json(filename):
    fp = gzip.open(os.path.join(FILES_PATH, 'yabormeparser', filename))
    borme.parser.importer.from_json_file(fp, set_url=False)
    return fp


# TODO: fixture for User, Profile, Customer and Subscription
class TestGenSubscription_BORME_A_2009_197_28(TestCase):

    fixtures = ["test_subscription.json"]

    def setUp(self):
        # self.fp_borme1 = gzip.open(os.path.join(FILES_PATH, 'yabormeparser', 'BORME-A-2009-197-28.json.gz'))
        self.fp_borme1 = load_borme_from_gzipped_json('BORME-A-2009-197-28.json.gz')
        self.fp_borme1.seek(0)
        self.borme_date = datetime.date(2009, 10, 15)
        self.borme_isodate = "2009-10-15"

        # self.user = User.objects.create_user('lennon@thebeatles.com', 'johnpassword')
        self.user = User.objects.first()
        self.subscription = Subscription.objects.first()

    def tearDown(self):
        self.fp_borme1.close()

    def test_import_adm(self):
        # Load BORME
        # borme.parser.importer.from_json_file(self.fp_borme1, set_url=False)
        #
        # Generate subscriptions for day
        results = alertas.parser.gen_subscription_event_from_borme('adm', self.fp_borme1)

        self.assertEqual(results['provincia'], "MADRID")
        self.assertEqual(results['cve'], "BORME-A-2009-197-28")
        self.assertEqual(results['date'], self.borme_isodate)

        n_subscriptions = SubscriptionEvent.objects.count()
        self.assertEqual(n_subscriptions, 0)

        # Import subscriptions
        alertas.importer.import_subscription_event(results)

        # TODO: check results ?

        n_subscriptions = SubscriptionEvent.objects.count()
        self.assertEqual(n_subscriptions, 1)

        subscription = SubscriptionEvent.objects.first()
        self.assertEqual(subscription.province, "28")
        self.assertEqual(subscription.event, "adm")
        self.assertEqual(subscription.event_date, datetime.date(2009, 10, 15))
        self.assertEqual(len(subscription.data_json), 47)

        for event in subscription.data_json:
            if event["company"]["name"] == "BURGFORD INVESTMENT SL":
                # FIXME: ending dot
                self.assertEqual(event["company"]["address"], "C/ ALFONSO XII - NUMERO 36 3º IZQUIERDA (MADRID).")
                self.assertEqual(event["company"]["nif"], "")
                self.assertEqual(event["company"]["url_api"], "https://api.librebor.me/v1/empresa/burgford-investment")
                self.assertEqual(event["company"]["url_web"], "https://librebor.me/borme/empresa/burgford-investment/")
                # FIXME: ending dot
                self.assertEqual(event["datos_registrales"], "T 22861 , F 161, S 8, H M 409334, I/A 6 (30.09.09).")
                self.assertEqual(event["new_roles"], [["ADM. UNICO", "PINILLA RISUEÑO RAUL"]])
            elif event["company"]["name"] == "ARIDOS EXTENDIDOS Y COMPACTACIONES SL":
                self.assertEqual(event["company"]["address"], "")
                self.assertEqual(len(event["new_roles"]), 2)

        # TODO: more checks

    def test_import_adm_twice(self):
        # Generate subscriptions for day
        results = alertas.parser.gen_subscription_event_from_borme('adm', self.fp_borme1)

        self.assertEqual(results['provincia'], "MADRID")
        self.assertEqual(results['cve'], "BORME-A-2009-197-28")
        self.assertEqual(results['date'], self.borme_isodate)

        n_subscriptions = SubscriptionEvent.objects.count()
        self.assertEqual(n_subscriptions, 0)

        # Import subscriptions
        alertas.importer.import_subscription_event(results)

        n_subscriptions = SubscriptionEvent.objects.count()
        self.assertEqual(n_subscriptions, 1)
        subscription = SubscriptionEvent.objects.first()
        self.assertEqual(len(subscription.data_json), 47)

        # Import subscriptions again
        alertas.importer.import_subscription_event(results)

        n_subscriptions = SubscriptionEvent.objects.count()
        self.assertEqual(n_subscriptions, 1)
        subscription = SubscriptionEvent.objects.first()
        self.assertEqual(len(subscription.data_json), 47)

    def test_send_subscriptions(self):
        results = alertas.parser.gen_subscription_event_from_borme('adm', self.fp_borme1)
        alertas.importer.import_subscription_event(results)

        # TODO: test email parameter
        total_sent = alertas.email.send_email_to_subscriber(
            'adm',
            self.borme_date
        )
        self.assertEqual(total_sent, 0)

        total_sent = alertas.email.send_email_to_subscriber(
            'adm',
            self.borme_date
        )
        self.assertEqual(total_sent, 0)
        self.assertEqual(len(mail.outbox), 0)

        subscriber = alertas.subscriptions.create(self.user, 'adm', 28, 'disabled', self.subscription)

        total_sent = alertas.email.send_email_to_subscriber(
            'adm',
            self.borme_date
        )
        self.assertEqual(total_sent, 0)
        self.assertEqual(len(mail.outbox), 0)

        subscriber.send_email = 'daily'
        subscriber.save()

        total_sent = alertas.email.send_email_to_subscriber(
            'adm',
            self.borme_date
        )
        self.assertEqual(total_sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Tus suscripciones en Librebor.me")
