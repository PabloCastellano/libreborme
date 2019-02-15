#!/usr/bin/env python3
#
# Example usage:
# 	./manage.py expire_test_users
#
# Expire a specific user without having into account date
# 	./manage.py expire_test_users --email user@example.com
#
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings

from alertas.email import send_expiration_email
from alertas.utils import get_alertas_config

from django.utils import timezone
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

User = get_user_model()


class Command(BaseCommand):
    help = 'Expire test accounts after X days from creation'
    fixtures = ['alertasconfig.json']

    def add_arguments(self, parser):
        parser.add_argument("--email")
        parser.add_argument("--silent", action='store_true', default=False,
                            help="Do not send email to the user")
        parser.add_argument("--dry-run", action='store_true', default=False,
                            help="Simulate. Don't do any action")

    def handle(self, *args, **options):
        self.options = options
        if options["verbosity"] > 1:
            LOG.setLevel(logging.DEBUG)

        if options['email']:
            user = User.objects.get(email=options["email"])
            if user.is_active:
                self.expire_user(user)
            else:
                LOG.info("User is already inactive")
        else:
            # Find users that joined days_test_subscription_expire days ago
            # and more
            days = int(get_alertas_config("days_test_subscription_expire"))
            date = timezone.now() - timezone.timedelta(days=days)
            users = User.objects.filter(date_joined__lte=date, is_active=True)
            if len(users) > 0:
                for user in users:
                    self.expire_user(user)
            else:
                LOG.info("No test users found to expire")

    def expire_user(self, user):
        LOG.info(
            "Expiring test user: {0} ({1})".format(user.email, user.get_full_name()))
        if not self.options["dry_run"]:
            do_send = not self.options["silent"]
            user.profile.expire_subscription(do_send)
