from django.core.management.base import BaseCommand
from borme.models import Company, Person


class Command(BaseCommand):
    args = '<person or company slug>'
    help = 'Show the sources where the information about some entity was retrieved'

    def handle(self, *args, **options):

        if len(args) != 1:
            print('Usage: bormesources <slug>')
            return

        try:
            entity = Person.objects.get(slug=args[0])
        except Person.DoesNotExist:
            try:
                entity = Company.objects.get(slug=args[0])
            except Company.DoesNotExist:
                print('Not found')
                return

        #print('{} appears in the following BORME gazettes:'.format(entity.name))
        for borme in entity.in_bormes:
            print(borme['url'])
