#!/usr/bin/env python3
#
# daily: must be run from Monday to Friday after the publication
# weekly: must be run from Friday after the publication to Sunday
# monthly: must be run on 1st day of the month
#
# Otherwise a CommandError exception is raised
#
# Example usage:
# 	./manage.py send_notifications weekly liq
#       ./manage.py send_notifications weekly liq -v 3
#
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.conf import settings
from django.db import connection
from django.template import loader
from alertas.models import AlertaActo, EVENTOS_DICT, PERIODICIDAD_DICT
from borme.utils import convertir_iniciales
from borme.templatetags.utils import slug2
from bormeparser.regex import is_acto_cargo

from bormeparser import Borme

import datetime
import logging
import os

TODAY = datetime.date.today()
BORME_JSON_PATH = os.path.expanduser("~/.bormes/json")
EMAIL_TEMPLATES_PATH = os.path.join("alertas", "templates", "email")

NOTIFICATION_SUBJECT = "Notificaciones de libreBORME ({}, {}, {})"
EMAIL_FROM = "noreply@libreborme.net"

ACTOS = {
    "liq": ("Liquidación"),
    "con": (),
    "new": ("Constitución", "Nueva sucursal"),
}


LOG = logging.getLogger(__file__)
LOG.setLevel(logging.INFO)

class Command(BaseCommand):
    help = 'Send periodic email subscriptions (AlertaActo only)'

    def add_arguments(self, parser):
        parser.add_argument("periodo")
        parser.add_argument("evento")
        parser.add_argument("--username", help="Notifications will be sent only to this user", default=None)
        parser.add_argument("--dry-run", action="store_true", default=False, help="Notifications are printed to stdout but not sent")

    def handle(self, *args, **options):
        periodo = options["periodo"]
        evento = options["evento"]

        ch = logging.StreamHandler()
        if options["verbosity"] > 1:
            LOG.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        LOG.addHandler(ch)

        # TODO: no es necesario, el backend puede ser EmailConsole
        if settings.DEBUG:
            LOG.info("forcing --dry-run since DEBUG=True\n")
            dry_run = False
        else:
            dry_run = options["dry_run"]

        if periodo not in ('daily', 'weekly', 'monthly'):
            print('Periodo {} is invalid. Valid values are: {}'.format(periodo, ', '.join(PERIODICIDAD_DICT.keys())))
            return
 
        if evento not in EVENTOS_DICT:
            print('Evento {} is invalid. Valid values are: {}'.format(evento, ', '.join(EVENTOS_DICT.keys())))
            return
        
        alertas = busca_subscriptores(periodo, evento, options["username"])
        if len(alertas) == 0:
            LOG.info("0 alertas. END")
            return

        companies = busca_empresas(periodo, evento)
        if len(companies) == 0:
            LOG.info("0 companies. END")
            return

        if dry_run:
            print("Notifications were not sent because --dry-run")
            return

        for alerta in alertas:
            if alerta.user.profile.notification_method == "email":
                send_email_notification(alerta, evento, periodo, companies)
            elif alerta.user.profile.notification_method == "url":
                send_url_notification(alerta, evento, periodo, companies)

        # TODO: añade a historial


def send_email_notification(alerta, evento, periodo, companies):
    email = alerta.user.profile.notification_email
    language = alerta.user.profile.language
    provincia = alerta.get_provincia_display()
    evento_display = alerta.get_evento_display()
    send_html = alerta.send_html

    if provincia not in companies:
        LOG.debug("No se envia a {} porque no hay alertas para {}/{}".format(email, provincia, evento))
        return False
    LOG.info("Se va a enviar a {} porque hay alertas para {}/{}".format(email, provincia, evento))

    companies = companies[provincia][evento]

    try:
        validate_email(email)
    except django.core.exceptions.ValidationError:
        LOG.error("User {} has an invalid notification email: {}. Nothing was sent to him!".format(alerta.user.get_full_name(), email))
        # Notify user about it
        # Add to history anyways
        return False

    template_name = os.path.join(settings.BASE_DIR, EMAIL_TEMPLATES_PATH, "alerta_acto_template_{lang}.txt".format(lang=language))
    context = {"companies": companies, "name": alerta.user.first_name, "provincia": provincia, "evento": evento_display, "date": TODAY}
    message = loader.render_to_string(template_name, context)
    html_message = None

    if send_html:
        template_name = os.path.join(settings.BASE_DIR, EMAIL_TEMPLATES_PATH, "alerta_acto_template_{lang}.html".format(lang=language))
        html_message = loader.render_to_string(template_name, context)

    today_format = TODAY.strftime("%d/%m/%Y")
    subject = NOTIFICATION_SUBJECT.format(today_format, evento_display, provincia)
    sent_emails = send_mail(subject,
                            message,
                            EMAIL_FROM,
                            [email],
                            html_message=html_message)
    return sent_emails == 1


# TODO: send_mass_email()
#message1 = ('Subject here', 'Here is the message', 'from@example.com', ['first@example.com', 'other@example.com'])
#message2 = ('Another Subject', 'Here is another message', 'from@example.com', ['second@test.com'])
#send_mass_mail((message1, message2), fail_silently=False)


def send_url_notification(alerta, evento, periodo, companies):
    endpoint_url = alerta.user.profile.notification_url
    # TODO
    raise NotImplementedError


def busca_evento(evento, begin_date, end_date):
    actos = {}
    total = 0
    cur_date = begin_date
    while cur_date <= end_date:
        borme_path = os.path.join(BORME_JSON_PATH, str(cur_date.year), "{:02d}".format(cur_date.month), "{:02d}".format(cur_date.day))
        if os.path.isdir(borme_path):
            files = os.listdir(borme_path)
            # LOG.debug(files)
            files = [os.path.join(borme_path, f) for f in files if f.endswith(".json")]
            for filepath in files:
                borme = Borme.from_json(filepath)
                for anuncio in borme.get_anuncios():
                    for acto in anuncio.actos:
                        if acto.name in ACTOS[evento]:
                            if borme.provincia.name not in actos:
                                actos[borme.provincia.name] = {"liq": [], "con": [], "new": []}
                            actos[borme.provincia.name][evento].append({"date": borme.date, "name": anuncio.empresa})
                            total += 1

        cur_date += datetime.timedelta(days=1)

    LOG.info("Total {} companies for event {} between {} and {}.".format(total, evento, begin_date, end_date))
    return (actos, total)


def busca_empresas(periodo, evento):
    if periodo == 'daily':
        if TODAY.weekday() in (5, 6):
            raise CommandError("Daily must not be run on Saturday nor Sunday")
        begin_date = TODAY
        end_date = TODAY
    elif periodo == 'weekly':
        if TODAY.weekday() not in (4, 5, 6):
            raise CommandError("Weekly must be run on Saturday or Sunday")
        begin_date = TODAY - datetime.timedelta(days=TODAY.weekday())  # Monday
        end_date = begin_date + datetime.timedelta(days=4)             # Friday
    elif periodo == 'monthly':
        if TODAY.day != 1:
            raise CommandError("Monthly must be run on the 1st day of the month")
        begin_date = datetime.date(TODAY.year, TODAY.month, 1)
        end_date = TODAY

    companies, total = busca_evento(evento, begin_date, end_date)

    provincias = sorted(companies.keys())
    #for provincia, data in companies.items():
    #    for company in data[evento]:
    #        LOG.debug("-- {name} ({provincia})".format(name=company["name"], provincia=provincia))
    LOG.debug("Found in provinces: {}".format(", ".join(provincias)))
    return companies


def busca_subscriptores(periodo, evento, username=None):
    alertas = AlertaActo.objects.filter(evento=evento, periodicidad=periodo, is_enabled=True)
    if username:
        alertas = alertas.filter(user__username=username)
    #for alerta in alertas:
    #    LOG.debug("-- {} <{}>".format(alerta.user.get_full_name(), alerta.user.email))
    LOG.info("Total {} alerts for event '{}'.".format(len(alertas), evento))
    return alertas
