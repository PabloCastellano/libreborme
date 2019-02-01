#!/usr/bin/env python3
#
# Example usage:
# 	./manage.py show_alertas_users
# 	./manage.py show_alertas_users -u usuario
#
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Show alertas users'

    def add_arguments(self, parser):
        parser.add_argument("--email")

    def handle(self, *args, **options):
        if options["email"]:
            try:
                user = User.objects.get(email=options["email"])
                print("Real name: {0}".format(user.get_full_name()))
                print("E-mail: {0}".format(user.email))
                print("Date joined: {0}".format(user.date_joined))
                print("Active: {0}".format(user.is_active))
            except User.DoesNotExist:
                print("User not found: {0}".format(options["email"]))
        else:
            users = User.objects.all()
            for user in users:
                if user.is_active:
                    print("* {0}".format(user.email))
                else:
                    print("* {0} (disabled)".format(user.email))
            print("Total: {0} users.".format(len(users)))
