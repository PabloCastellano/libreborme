from django.core.management.base import BaseCommand
from borme.models import Company, Person


class Command(BaseCommand):
    help = 'Show the sources where the information about some entity was retrieved'

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str, help="person or company slug")

    def handle(self, *args, **options):

        try:
            entity = Person.objects.get(slug=options["slug"])
        except Person.DoesNotExist:
            try:
                entity = Company.objects.get(slug=options["slug"])
            except Company.DoesNotExist:
                print('Not found')
                return

        for borme in entity.in_bormes:
            print(borme['url'])
