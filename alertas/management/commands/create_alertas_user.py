#!/usr/bin/env python3
#
# Example usage:
# 	./manage.py create_alertas_user weekly liq
#
# TODO: send email
# TODO: crear factura?
# TODO: crear alerta de prueba?
# TODO: generate random password and show/email it
#
from django.core.management.base import BaseCommand, CommandError

from alertas.utils import create_alertas_user

import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Create a new customer account for alertas'

    def add_arguments(self, parser):
        parser.add_argument("--email")
        parser.add_argument("--first_name")
        parser.add_argument("--last_name")
        parser.add_argument("--password")

    def handle(self, *args, **options):
        ch = logging.StreamHandler()
        if options["verbosity"] > 1:
            LOG.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        LOG.addHandler(ch)

        if not options['email']:
            email = input("Please enter email: ")
        else:
            email = options["email"]

        if not options['first_name']:
            first_name = input("Please enter first name: ")
        else:
            first_name = options["first_name"]

        if not options["last_name"]:
            last_name = input("Please enter last name: ")
        else:
            last_name = options["last_name"]

        if not options["password"]:
            password = input("Please enter password: ")
        else:
            password = options["password"]

        create_alertas_user(email, password, first_name, last_name)
