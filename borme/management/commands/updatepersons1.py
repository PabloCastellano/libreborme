# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from borme.models import Company, Person, EmbeddedCompany
from mongoengine.errors import ValidationError, NotUniqueError

import time


class Command(BaseCommand):
    help = 'Add field person.in_companies2'

    def handle(self, *args, **options):
        start_time = time.time()
        for person in Person.objects:
            print person
            companies_list = []
            for company_slug in person.in_companies:
                c = Company.objects.get(slug=company_slug)
                companies_list.append(EmbeddedCompany(name=c.name, slug=company_slug))
            person.in_companies2 = companies_list
            person.save()

        # Elapsed time
        elapsed_time = time.time() - start_time
        print '\nElapsed time: %.2f seconds' % elapsed_time
