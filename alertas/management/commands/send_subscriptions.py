#!/usr/bin/env python3
#
# Example usage:
# 	./manage.py send_subscriptions adm
#   ./manage.py send_subscriptions liq -v 3
#
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

import alertas.email

import datetime
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Send periodic email subscriptions (UserSubscription)'

    def add_arguments(self, parser):
        parser.add_argument("evento")
        parser.add_argument("--email", help="Notifications will be sent only to this user", default=None)
        parser.add_argument("--date", help='ISO formatted date (ex. 2016-01-01)')

    def handle(self, *args, **options):
        evento = options["evento"]

        ch = logging.StreamHandler()
        if options["verbosity"] > 1:
            alertas.email.LOG.setLevel(logging.DEBUG)
            LOG.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        LOG.addHandler(ch)

        if options["date"]:
            date = parse_date(options["date"])
        else:
            date = datetime.date.today()

        total_sent = alertas.email.send_email_to_subscriber(
            evento,
            date,
            options["email"]
        )

        LOG.info("{} emails were sent".format(total_sent))
