from django.core.management.base import BaseCommand
from borme.models import Person


class Command(BaseCommand):
    args = '<person name or slug ...>'
    help = 'Find a person and show its information'

    def handle(self, *args, **options):
        for person_name in args:

            persons = Person.objects.filter(name__icontains=person_name)
            if not persons:
                persons = Person.objects.filter(slug__icontains=person_name)

            for person in persons:
                bormes = list(map(lambda c: c['cve'], person.in_bormes))
                print('Name:', person.name)
                print('Slug:', person.slug)
                print('Companies:', ', '.join(person.in_companies))
                print('BORMEs:', ', '.join(bormes))
                print('Last modified:', person.date_updated)
                print()

            print('Found %d ocurrences with keyword "%s"' % (len(persons), person_name))
            print()
