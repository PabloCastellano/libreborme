from django.core.management.base import BaseCommand
from borme.models import Company


class Command(BaseCommand):
    help = 'Find a company and show its information'

    def add_arguments(self, parser):
        parser.add_argument("keyword", type=str, help="company keyword")

    def handle(self, *args, **options):
        keyword = options["keyword"]

        results = Company.objects.filter(name__icontains=keyword)
        if not results:
            results = Company.objects.filter(slug__contains=keyword)

        for company in results:
            bormes = list(map(lambda c: c['cve'], company.in_bormes))
            print("Name: {}".format(company.name))
            print("Slug: {}".format(company.slug))
            print("BORMEs: {}".format(", ".join(bormes)))
            print("Last modified: {}".format(company.date_updated))
            print()

        print('Found {} ocurrences with keyword "{}"'.format(len(results), keyword))
        print()
