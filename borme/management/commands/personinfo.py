from django.core.management.base import BaseCommand, CommandError
from borme.models import Person

class Command(BaseCommand):
    args = '<company name or slug ...>'
    help = 'Shows info about a company'

    def handle(self, *args, **options):
        for company_name in args:
            try:
                person = Person.objects.get(name=company_name)
            except Company.DoesNotExist:
                try:
                    person = Person.objects.get(slug=company_name)
                except Company.DoesNotExist:
                   raise CommandError('Person "%s" does not exist' % company_name)

            print 'Name:', person.name
            print

            self.stdout.write('Successful operation!')
