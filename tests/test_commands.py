from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from alertas.models import Profile
from alertas.utils import create_alertas_user, get_alertas_config


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
        profiles = User.objects.all()
        self.assertEqual(len(profiles), 1)

        user = User.objects.first()
        self.assertEqual(user.username, "fred")
        self.assertEqual(user.email, "fred@localhost")
        self.assertEqual(user.first_name, "Fred")
        self.assertEqual(user.last_name, "Foo")

        profile = Profile.objects.first()
        self.assertEqual(profile.account_type, "test")
        self.assertEqual(profile.notification_method, "email")
        self.assertEqual(profile.notification_email, "fred@localhost")


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


"""
class TestCommandNotifications(TestCase):
    
    def test_send_notifications(self):
        self.assertEqual(1, 1)

        call_command('send_notifications')

        # test emails sent
"""