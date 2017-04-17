#!/usr/bin/env python3
#
# Example usage:
# 	./manage.py create_alertas_user weekly liq
#
# TODO: send email
# TODO: check type argument
# TODO: crear factura?
# TODO: crear alerta de prueba?
#
from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User

from alertas.models import Profile
import logging

LOG = logging.getLogger(__file__)
LOG.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Send periodic email subscriptions (AlertaActo only)'

    def add_arguments(self, parser):
        parser.add_argument("--username")
        parser.add_argument("--email")
        parser.add_argument("--type", default="test")

    def handle(self, *args, **options):
        ch = logging.StreamHandler()
        if options["verbosity"] > 1:
            LOG.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        LOG.addHandler(ch)

        if not options['username']:
            username = input("Please enter username: ")
        else:
            username = options["username"]

        if 'email' in options:
            email = input("Please enter email: ")
        else:
            email = options["email"]

        first_name = input("Please enter first name: ")
        last_name = input("Please enter last name: ")
        password = input("Please enter password: ")

        new_user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)

        profile = Profile(user=new_user, account_type=options["type"], notification_email=email)
        profile.save()
