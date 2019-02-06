#!/usr/bin/env python3
#
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Template

from alertas.models import Follower

from borme.models import Company, Person
from libreborme.models import MailTemplate
from bormeparser.config import CONFIG as borme_config

import csv
import datetime
import logging
import os
import time

TODAY = datetime.date.today()

LOG = logging.getLogger(__file__)
LOG.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Followers CLI'

    def add_arguments(self, parser):
        parser.add_argument("--list", action="store_true", help="List all followers")
        parser.add_argument("--today", action="store_true", help="Followers notified today")
        parser.add_argument("--modif-people", action="store_true", help="People modified today")
        parser.add_argument("--modif-companies", action="store_true", help="Companies modified today")
        parser.add_argument("--send", action="store_true", help="Send alerts")

    def handle(self, *args, **options):

        ch = logging.StreamHandler()
        if options["verbosity"] > 1:
            LOG.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        LOG.addHandler(ch)

        today = datetime.date.today()
        today = datetime.date(2018, 3, 13)
        if options["list"]:
            list_followers(output=True)
        elif options["modif_people"]:
            list_modified_people(today, output=True)
        elif options["modif_companies"]:
            list_modified_companies(today, output=True)
        elif options["today"]:
            list_notified_day(today)
        elif options["send"]:
            send(today)


def list_followers(output=False):
    followers = Follower.objects.all()
    for f in followers:
        if output:
            print(f)
    print("Total: {} followers".format(len(followers)))
    return followers


def list_modified_people(day, output=False):
    people = Person.objects.filter(date_updated=day)
    for p in people:
        if output:
            print(p)
    print("Total: {} people".format(len(people)))
    return people


def list_modified_companies(day, output=False):
    companies = Company.objects.filter(date_updated=day)
    for c in companies:
        if output:
            print(c)
    print("Total: {} companies".format(len(companies)))
    return companies


def list_notified_day(day):
    companies = list_modified_companies(day)
    people = list_modified_people(day)
    followers = list_followers()
    notifications = {}
    for f in followers:
        f_c = [c for c in companies if c.slug == f.slug and f.type == 'company']
        f_p = [p for p in people if p.slug == p.slug and f.slug == 'person']
        total = len(f_c + f_p)
        if any([f_c, f_p]):
            for n in f_c + f_p:
                notifications.setdefault(f.user, [])
                notifications[f.user].extend(f_c + f_p)

    print("Notifications")
    for user, entities in notifications.items():
        print("User {} will be notified about {} entities:".format(user.email, len(entities)))
        for e in entities:
            print("* " + e.name + " (" + e.slug + ")")
    print("Total: {} notifications".format(len(notifications)))
    return notifications


def prepare_emails(notifications):
    datatuple = []
    from_email = "contacto@libreborme.net"
    subject = "La empresa que sigue ha hecho cosas"
    for user, entities in notifications.items():
        template = MailTemplate.objects.get(name="follow_alert")
        if user.profile.send_html:
            tpl = Template(template.html_text)
        else:
            tpl = Template(template.plain_text)
        placeholders = {
            "user": user.get_full_name(),
            "total": len(entities),
            "entities": entities
        }
        content = tpl.render(Context(placeholders))
        datatuple.append((subject, content, from_email, [user.email]))
    return datatuple


def send(day):
    notifications = list_notified_day(day)
    emails = prepare_emails(notifications)
    total_sent = send_mass_mail(emails)
    print("Total: {} emails sent".format(total_sent))
