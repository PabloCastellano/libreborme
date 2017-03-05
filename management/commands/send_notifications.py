#!/usr/bin/env python3
#
# daily: must be run from Monday to Friday after the publication
# weekly: must be run from Friday after the publication to Sunday
# monthly: must be run on 1st day of the month
#
# Otherwise a CommandError exception is raised

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_email
from django.conf import settings
from django.db import connection
from django.template import loader
from alertas.models import EVENTOS_DICT, PERIODICIDAD_DICT
from borme.models import Anuncio, Company, Person
from borme.utils import convertir_iniciales
from borme.templatetags.utils import slug2
from bormeparser.regex import is_acto_cargo

import datetime
import logging
import os

BORME_JSON_PATH = os.expand("~/.bormes/json")

ACTOS {
    "liq": ("Liquidación"),
    "con": (),
    "new": ("Constitución", "Nueva sucursal"),
}


LOG = logging.get_logger(__file__)


class Command(BaseCommand):
    #args = '<PERIODO> <EVENTO> [--dry-run] [user]'
    help = 'Send monthly email subscriptions (AlertaActo only)'

    def add_arguments(self, parser):
        parser.add_argument("periodo")
        parser.add_argument("evento")
        #parser.add_argument("--user", help="If specified, notifications will be sent only to this user")
        parser.add_argument("--dry-run", action="store_true", default=False, help="Notifications are printed to stdout but not sent")

    def handle(self, *args, **options):

        #if len(args) != 1:
        #    print('Usage: bormehide <slug>')
        #    return

        periodo = options["periodo"]
        evento = options["evento"]

        # TODO: no es necesario, el backend puede ser EmailConsole
        if settings.DEBUG:
            LOG.info("forcing --dry-run since DEBUG=True")
            dry_run = False
        else:
            dry_run = options["dry_run"]

        if periodo not in ('daily', 'weekly', 'monthly'):
            print('Periodo {} is invalid. Valid values are: {}'.format(periodo, ', '.join(PERIODICIDAD_DICT.keys()))
            return
 
        if evento not in EVENTOS_DICT:
            print('Evento {} is invalid. Valid values are: {}'.format(evento, ', '.join(EVENTOS_DICT.keys())))
            return
        
        companies = busca_empresas(periodo, evento)
        alertas = busca_subscriptores(periodo, evento)
        LOG.info("Total {} companies for event {}.".format(len(companies), evento))
        LOG.info("Total {} users are subscribed to this event and will be notified.".format(len(users), evento))

        if dry_run:
            print("Notifications were not sent because --dry-run")
            return

        for alerta in alertas:
            if user.notification_method == "email":
                send_email_notification(user, evento, periodo, companies)
            elif user.notification_method == "url":
                send_url_notification(user, evento, periodo, companies)

        # TODO: añade a historial


def send_email_notification(alerta, evento, periodo, companies):
    email = alerta.user.profile.notification_email
    language = alerta.user.language
    provincia = alerta.provincia
    send_html = alerta.send_html
    companies = companies[provincia][evento]

    template_name = "alertas/email/alerta_acto_template_{lang}.txt".format(lang=language)
    message = loader.render_to_string(template_name, {"objects": companies, "name": alerta.user.name})
    html_message = None

    if send_html:
        template_name = "alertas/email/alerta_acto_template_{lang}.html".format(lang=language)
        html_message = loader.render_to_string(template_name, {"objects": companies, "name": alerta.user.name})

    LOG.debug("Sending email to {}".format(email))
    alerta.user.send_mail("Notificaciones de libreborme",
                          message,
                          "noreply@libreborme.net",
                          email,
                          html_message=html_message)


# TODO: send_mass_email()
#message1 = ('Subject here', 'Here is the message', 'from@example.com', ['first@example.com', 'other@example.com'])
#message2 = ('Another Subject', 'Here is another message', 'from@example.com', ['second@test.com'])
#send_mass_mail((message1, message2), fail_silently=False)


def send_url_notification(user, evento, periodo, companies):
    endpoint_url = alerta.user.profile.notification_url


def busca_evento(evento, begin_date, end_date):
    LOG.info("Buscando eventos de tipo {} del {} al {}".format(evento, begin_date, end_date))
    actos = {}
    cur_date = begin_date
    while cur_date <= end_date
        borme_path = os.path.join(BORME_JSON_PATH, cur_date.year, cur_date.month, cur_date.day)
        if os.path.isdir(borme_path):
            files = os.listdir(borme_path)
            LOG.debug(files)
            files = [os.path.join(borme_path, f) for f in files if f.endswith(".json")]
            for filepath in files:
                borme = Borme.load(filepath)
                for acto in borme.get_actos():
                    if acto.name in ACTOS[evento]:
                        if borme.provincia not in actos:
                            actos[borme.provincia = []
                        actos[borme.provincia].append({"date": borme.date, "company": acto})

        cur_date += datetime.timedelta(days=1)

    return actos


def busca_empresas(periodo, evento):
    today = datetime.date.today()

    if periodo == 'daily':
        if today.weekday() in (5, 6):
            raise CommandError("Daily must not be run on Saturday nor Sunday")
        begin_date = today
        end_date = today
    elif periodo == 'weekly':
        if today.weekday() not in (4, 5, 6):
            raise CommandError("Weekly must be run on Saturday or Sunday")
        begin_date = today - datetime.timedelta(days=today.weekday())  # Monday
        end_date = begin_date + datetime.timedelta(days=4)             # Friday
    elif periodo == 'monthly':
        if today.day != 1:
            raise CommandError("Monthly must be run on the 1st day of the month")
        begin_date = datetime.date(today.year, today.month, 1)
        end_date = today

    companies = busca_evento(evento, begin_date, end_date)
    return companies


def busca_subscriptores(periodo, evento):
    alertas = AlertaActo.objects.filter(evento=evento, periodicidad=periodo, is_enabled=True)
    # join .user
    LOG.info("Se han encontrado {} suscriptores.".format(len(alertas)))
    # TODO: if LOG.debug_level == logging.DEBUG
    for alerta in alertas:
        LOG.debug("-- {} <{}>".format(alerta.user.get_full_name(), alerta.user.email))
    return alertas
