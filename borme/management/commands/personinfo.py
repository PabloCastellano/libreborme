from django.core.management.base import BaseCommand, CommandError
from borme.models import Person


class Command(BaseCommand):
    help = 'Shows info about a person'

    def add_arguments(self, parser):
        parser.add_argument("person", type=str, help="person name or slug")

    def handle(self, *args, **options):
        person = options["person"]
        try:
            result = Person.objects.get(name=person)
        except Person.DoesNotExist:
            try:
                result = Person.objects.get(slug=person)
            except Person.DoesNotExist:
                raise CommandError('Person "%s" does not exist' % person)

        print("Name: {}".format(result.name))
        print("Slug: {}".format(result.slug))
        print()
