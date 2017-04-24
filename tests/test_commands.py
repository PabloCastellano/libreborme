from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from alertas.models import AlertaActo, AlertaHistory, Profile
from alertas.utils import create_alertas_user, get_alertas_config
from bormeparser.config import CONFIG as borme_config

import os.path

THIS_PATH = os.path.dirname(os.path.abspath(__file__))


class TestCommandCreateAlertasUser(TestCase):

    def test_user_is_created(self):
        users = User.objects.all()
        self.assertEqual(len(users), 0)
        profiles = Profile.objects.all()
        self.assertEqual(len(profiles), 0)

        call_command('create_alertas_user', username="fred", email="fred@localhost",
                     first_name='Fred', last_name="Foo", password="secret")

        users = User.objects.all()
        self.assertEqual(len(users), 1)
        profiles = Profile.objects.all()
        self.assertEqual(len(profiles), 1)

        user = User.objects.first()
        self.assertEqual(user.username, "fred")
        self.assertEqual(user.email, "fred@localhost")
        self.assertEqual(user.first_name, "Fred")
        self.assertEqual(user.last_name, "Foo")
        self.assertEqual(user.profile.account_type, "test")
        self.assertEqual(user.profile.notification_method, "email")
        self.assertEqual(user.profile.notification_email, "fred@localhost")


class TestCommandExpireTest(TestCase):

    fixtures = ['alertasconfig.json']

    @classmethod
    def setUpClass(cls):
        super(TestCommandExpireTest, cls).setUpClass()

        create_alertas_user("fred", "fred@localhost", "secret", "Fred", "Foo", "test")
        john = create_alertas_user("john", "john@localhost", "secret", "John", "Foo", "test")
        days = int(get_alertas_config("days_test_subscription_expire"))
        john.date_joined = timezone.now() - timezone.timedelta(days=days)
        john.save()

    def test_user_expired(self):
        users = User.objects.filter(is_active=True)
        self.assertEqual(len(users), 2)

        call_command('expire_test_users')

        users = User.objects.filter(is_active=True)
        self.assertEqual(len(users), 1)

        john = User.objects.get(username="john")
        self.assertEqual(john.is_active, False)


# Es difícil testear pq no se guardan los datos en la BD
# Se parsean los json
# Hay que mockear el path y la fecha actual para que coja bien el path
# 
# El parser de BORME-JSONs y generador de alertas podría ser mejor un Job de Luigi, que metiera en la BD los valores y luego
#  una función que leyera estos valores. O un parser que creara un archivo intermedio y se pudiera importar en la BD.
"""
class TestCommandNotifications(TestCase):
    # En lugar de comprobar si se ha enviado el email, comprobamos si existe el historial

    def setUp(self):
        self.john = create_alertas_user("john", "john@localhost", "secret", "John", "Foo", "test")
        AlertaActo.objects.create(user=self.john, evento="liq", provincia="Lugo", periodicidad="daily")
        AlertaActo.objects.create(user=self.john, evento="liq", provincia="Lugo", periodicidad="weekly")
        AlertaActo.objects.create(user=self.john, evento="new", provincia="Lugo", periodicidad="weekly")
        AlertaActo.objects.create(user=self.john, evento="new", provincia="Lugo", periodicidad="monthly")
        borme_config["borme_root"] = os.path.join(THIS_PATH, 'files', 'BORME-A-2017-76-03.json')

    def test_send_notifications(self):
        history = AlertaHistory.objects.all()
        self.assertEqual(len(history), 0)

        call_command('send_notifications', "daily", "liq")
        call_command('send_notifications', "weekly", "liq")
        call_command('send_notifications', "weekly", "new")
        call_command('send_notifications', "monthly", "new")

        history = AlertaHistory.objects.filter(periodicidad="daily")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].type, "liq")
        self.assertEqual(history[0].user, "john")
        #self.assertEqual(history[0].date, "TODO")

        history = AlertaHistory.objects.filter(periodicidad="weekly")
        self.assertEqual(len(history), 2)
        self.assertEqual((history[0].type, history[1].type), ("liq", "new"))
        self.assertEqual(history[0].user, "john")
        self.assertEqual(history[1].user, "john")

        history = AlertaHistory.objects.filter(periodicidad="monthly")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].type, "new")
        self.assertEqual(history[0].user, "john")
"""