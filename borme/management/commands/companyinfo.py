from django.core.management.base import BaseCommand, CommandError
from borme.models import Company


class Command(BaseCommand):
    help = 'Shows info about a company'

    def add_arguments(self, parser):
        parser.add_argument("company", type=str, help="company name or slug")

    def handle(self, *args, **options):
        company = options["company"]
        try:
            result = Company.objects.get(name=company)
        except Company.DoesNotExist:
            try:
                result = Company.objects.get(slug=company)
            except Company.DoesNotExist:
                raise CommandError('Company "%s" does not exist' % company)

        print("Name: {}".format(result.name))
        print("Slug: {}".format(result.slug))
        print("Date: {}".format(result.date_creation))
        print("Active: {}".format(result.is_active))
        print()
