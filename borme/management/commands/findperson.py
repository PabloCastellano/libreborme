from django.core.management.base import BaseCommand
from borme.models import Person


class Command(BaseCommand):
    help = 'Find a person and show its information'

    def add_arguments(self, parser):
        parser.add_argument("keyword", type=str, help="person keyword")

    def handle(self, *args, **options):
        keyword = options["keyword"]

        results = Person.objects.filter(name__icontains=keyword)
        if not results:
            results = Person.objects.filter(slug__icontains=keyword)

        for person in results:
            bormes = list(map(lambda c: c['cve'], person.in_bormes))
            print("Name: {}".format(person.name))
            print("Slug: {}".format(person.slug))
            print("Companies: {}".format(", ".join(person.in_companies)))
            print("BORMEs: {}".format(", ".join(bormes)))
            print("Last modified: {}".format(person.date_updated))
            print()

        print('Found {} ocurrences with keyword "{}"'.format(len(results), keyword))
        print()
