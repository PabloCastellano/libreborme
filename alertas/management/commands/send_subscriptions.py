#!/usr/bin/env python3
#
# daily: must be run from Monday to Friday after the publication
# weekly: must be run from Friday after the publication to Sunday
# monthly: must be run on 1st day of the month
#
# It generates the alerts by parsing BORME-JSON files. It doesn't take into account data in the database
#
# Otherwise a CommandError exception is raised
#
# Example usage:
# 	./manage.py send_notifications weekly liq
#   ./manage.py send_notifications weekly liq -v 3
#
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from alertas.email import send_email_notification
from alertas.models import AlertaActo, EVENTOS_DICT, PERIODICIDAD_DICT

from borme.templatetags.utils import slug2
from bormeparser import Borme
from bormeparser.config import CONFIG as borme_config

import csv
import datetime
import json
import logging
import os
import time

TODAY = datetime.date.today()

LOG = logging.getLogger(__file__)
LOG.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Send periodic email subscriptions (AlertaActo)'

    def add_arguments(self, parser):
        # parser.add_argument("periodo")
        parser.add_argument("evento")
        parser.add_argument("--email", help="Notifications will be sent only to this user", default=None)
        parser.add_argument("--dry-run", action="store_true", default=False, help="Notifications are printed to stdout but not sent")

    def handle(self, *args, **options):
        # periodo = options["periodo"]
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

        """
        if periodo not in ('daily', 'weekly', 'monthly'):
            print('Periodo {} is invalid. Valid values are: {}'.format(periodo, ', '.join(PERIODICIDAD_DICT.keys())))
            return
        """

        if evento not in EVENTOS_DICT:
            print('Evento {} is invalid. Valid values are: {}'.format(evento, ', '.join(EVENTOS_DICT.keys())))
            return

        # show_warning_date(periodo)

        alertas = busca_subscriptores(evento, options["email"])
        if len(alertas) == 0:
            LOG.info("0 alertas. END")
            return

        """
        companies = busca_empresas(periodo, evento)
        if len(companies) == 0:
            LOG.info("0 companies. END")
            return

        # Generar los CSV
        generar_csv(evento, periodo, companies)
        """

        if dry_run:
            print("Notifications were not sent because --dry-run")
            return

        for alerta in alertas:
            subject = "Tus subscripciones"
            month = '{:02d}'.format(TODAY.month)
            day = '{:02d}'.format(TODAY.day)
            filename = "/home/libreborme/subscriptions/{year}/{month}/{day}/{provincia}.json".format(
                    year=TODAY.year, month=month, day=day, provincia=alerta.provincia)
            if not os.path.exists(filename):
                print("No file exists for this province today")
                continue
            with open(filename) as fp:
                content = json.load(fp)
            message = str(content)
            alerta.user.email_user(subject, message)
            """
            if alerta.user.profile.notification_method == "email":
                send_email_notification(alerta, evento, periodo, companies, TODAY)
            elif alerta.user.profile.notification_method == "url":
                send_url_notification(alerta, evento, periodo, companies)
            """


def generar_csv(evento, periodo, companies):
    # Formato CSV:
    #   Fecha,Nombre,Provincia,Fecha,Evento,
    #   2017-02-01,Patatas SL,Valencia,Empresas de nueva creación
    #
    # Si weekly/monthly:
    #   Fecha,Nombre,Provincia,Evento,
    #   2017-02-01,Patatas SL,Valencia,Empresas de nueva creación
    #   2017-02-02,Patatas SL,Valencia,Empresas de nueva creación
    #   2017-02-03,Patatas SL,Valencia,Empresas de nueva creación
    #   ...
    #
    # alerta.user
    begin_date, end_date = get_rango_fechas(periodo)
    year = str(end_date.year)
    month = "{:02d}".format(end_date.month)
    day = "{:02d}".format(end_date.day)
    evento_name = EVENTOS_DICT[evento]

    for provincia, alertas in companies.items():
        # one CSV per each provincia
        path = os.path.join(settings.BORME_ROOT, "csv_alertas", provincia.replace(" ", "_"), periodo, year, month)
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, day + "_" + evento + ".csv")

        with open(filepath, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Fecha", "Nombre", "Provincia", "Evento"])
            for alerta in alertas:
                csvwriter.writerow([alerta["date"], alerta["name"], provincia, evento_name])

        print("Written " + filepath)


def send_url_notification(alerta, evento, periodo, companies):
    # endpoint_url = alerta.user.profile.notification_url
    # TODO
    pass


def busca_evento(begin_date, end_date, evento):
    actos = {}
    total = 0
    already_added = []
    cur_date = begin_date
    while cur_date <= end_date:
        borme_path = os.path.join(borme_config["borme_root"], str(cur_date.year), "{:02d}".format(cur_date.month), "{:02d}".format(cur_date.day))
        if os.path.isdir(borme_path):
            files = os.listdir(borme_path)
            # LOG.debug(files)
            files = [os.path.join(borme_path, f) for f in files if f.endswith(".json")]
            for filepath in files:
                borme = Borme.from_json(filepath)
                if borme.provincia.name not in actos:
                    actos[borme.provincia.name] = []
                for anuncio in borme.get_anuncios():
                    # En liquidación
                    if evento == "liq":
                        if anuncio.liquidacion:
                            actos[borme.provincia.name].append({"date": borme.date, "name": anuncio.empresa, "slug": slug2(anuncio.empresa)})
                            total += 1
                    # Empresas de nueva creación
                    if evento == "new":
                        for acto in anuncio.actos:
                            if acto.name in ("Constitución", "Nueva sucursal"):
                                actos[borme.provincia.name].append({"date": borme.date, "name": anuncio.empresa, "slug": slug2(anuncio.empresa)})
                                total += 1
                    # Concursos de acreedores
                    if evento == "con":
                        for acto in anuncio.actos:
                            if acto.name == "Situación concursal":
                                slug = slug2(anuncio.empresa)
                                if slug not in already_added:
                                    already_added.append(slug)
                                    actos[borme.provincia.name].append({"date": borme.date, "name": anuncio.empresa, "slug": slug})
                                    total += 1
        cur_date += datetime.timedelta(days=1)

    return (actos, total)


"""
def show_warning_date(periodo):
    if periodo == 'daily' and TODAY.weekday() in (5, 6):
        LOG.warn("Daily must not be run on Saturday nor Sunday")
    elif periodo == 'weekly' and TODAY.weekday() not in (4, 5, 6):
        LOG.warn("Weekly must be run on Saturday or Sunday")
    elif periodo == 'monthly' and TODAY.day != 1:
        LOG.warn("Monthly must be run on the 1st day of the month")
    time.sleep(5)


def get_rango_fechas(periodo):
    if periodo == 'daily':
        begin_date = TODAY
        end_date = TODAY
    elif periodo == 'weekly':
        begin_date = TODAY - datetime.timedelta(days=TODAY.weekday())  # Monday
        end_date = begin_date + datetime.timedelta(days=4)             # Friday
    elif periodo == 'monthly':
        begin_date = datetime.date(TODAY.year, TODAY.month, 1)
        end_date = TODAY
    return (begin_date, end_date)


def busca_empresas(periodo, evento):
    begin_date, end_date = get_rango_fechas(periodo)

    if evento in ("liq", "new"):
        companies, total = busca_evento(begin_date, end_date, evento)
    LOG.info("{} companies found for event '{}' between {} and {}".format(total, evento, begin_date, end_date))

    provincias = sorted(companies.keys())
    #for provincia, data in companies.items():
    #    for company in data[evento]:
    #        LOG.debug("-- {name} ({provincia})".format(name=company["name"], provincia=provincia))
    LOG.debug("Found in provinces: {}".format(", ".join(provincias)))

    return companies
"""

def busca_subscriptores(evento, email=None):
    alertas = AlertaActo.objects.filter(evento=evento, is_enabled=True, user__is_active=True)
    if email:
        alertas = alertas.filter(user__email=email)
    LOG.info("Total {} subscribers for event '{}' (use -v 3 for more information).".format(len(alertas), evento))
    for alerta in alertas:
        LOG.debug("#{0}: {1} <{2}>".format(alerta.id, alerta.user.get_full_name(), alerta.user.email))
    return alertas
