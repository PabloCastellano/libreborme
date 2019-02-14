#!/usr/bin/env python3
#
# Example usage:
# 	./manage.py send_subscriptions adm
#   ./manage.py send_subscriptions liq -v 3
#
from django.core.management.base import BaseCommand
from django.conf import settings

from alertas.email import send_email_to_subscriber
from alertas.models import UserSubscription, EVENTOS_DICT

import datetime
import json
import logging
import os

TODAY = datetime.date.today()

LOG = logging.getLogger(__file__)
LOG.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Send periodic email subscriptions (UserSubscription)'

    def add_arguments(self, parser):
        parser.add_argument("evento")
        parser.add_argument("--email", help="Notifications will be sent only to this user", default=None)
        parser.add_argument("--dry-run", action="store_true", default=False, help="Notifications are printed to stdout but not sent")

    def handle(self, *args, **options):
        evento = options["evento"]

        ch = logging.StreamHandler()
        if options["verbosity"] > 1:
            LOG.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        LOG.addHandler(ch)

        if evento not in EVENTOS_DICT:
            print('Evento {} is invalid. Valid values are: {}'.format(evento, ', '.join(EVENTOS_DICT.keys())))
            return

        alertas = busca_suscriptores(evento, options["email"])
        if len(alertas) == 0:
            LOG.info("0 alertas. END")
            return

        if options['dry_run']:
            print("Notifications were not sent because --dry-run")
            return

        for alerta in alertas:
            send_email_to_subscriber(alerta, evento, TODAY)
            """
            if alerta.user.profile.notification_method == "email":
                send_email_notification(alerta, evento, companies, TODAY)
            elif alerta.user.profile.notification_method == "url":
                send_url_notification(alerta, evento, companies)
            """


def busca_suscriptores(evento, email=None):
    alertas = UserSubscription.objects.filter(evento=evento, is_enabled=True,
                                        user__is_active=True)
    if email:
        alertas = alertas.filter(user__email=email)
    LOG.info("Total {} subscribers for event '{}' (use -v 3 for more information).".format(len(alertas), evento))
    LOG.debug(EVENTOS_DICT[evento])
    for alerta in alertas:
        LOG.debug("#{0}: {1} <{2}> ({3})".format(alerta.id, alerta.user.get_full_name(), alerta.user.email, alerta.get_provincia_display()))
    return alertas
