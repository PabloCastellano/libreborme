from django.test import TestCase

from alertas.models import LibrebormeLogs
from alertas.utils import create_alertas_user


class TestProfile(TestCase):

    fixtures = ['alertasconfig.json']

    def setUp(self):
        self.user = create_alertas_user("john@localhost", "secret", "John", "Foo")

    def test_expire_subscription(self):
        logs = LibrebormeLogs.objects.all()
        self.assertTrue(self.user.is_active)
        self.assertEqual(len(logs), 0)

        self.user.profile.expire_subscription(send_email=True)

        self.assertFalse(self.user.is_active)
        logs = LibrebormeLogs.objects.all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].component, "subscription")
