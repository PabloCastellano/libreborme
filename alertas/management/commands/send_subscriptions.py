#!/usr/bin/env python3
#
# Example usage:
# 	./manage.py send_subscriptions adm
#   ./manage.py send_subscriptions liq -v 3
#
from django.core.management.base import BaseCommand

import alertas.email

import datetime
import logging

TODAY = datetime.date.today()

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Send periodic email subscriptions (UserSubscription)'

    def add_arguments(self, parser):
        parser.add_argument("evento")
        parser.add_argument("--email", help="Notifications will be sent only to this user", default=None)

    def handle(self, *args, **options):
        evento = options["evento"]

        ch = logging.StreamHandler()
        if options["verbosity"] > 1:
            LOG.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        LOG.addHandler(ch)

        total_sent = alertas.email.send_email_to_subscriber(
            evento,
            TODAY,
            options["email"]
        )

        LOG.info("{} emails were sent".format(total_sent))
