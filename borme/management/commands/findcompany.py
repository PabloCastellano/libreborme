from django.core.management.base import BaseCommand, CommandError
from borme.models import Company

class Command(BaseCommand):
    args = '<company name or slug ...>'
    help = 'Shows info about a company'

    def handle(self, *args, **options):
        for company_name in args:
            try:
                companies = Company.objects.filter(name__contains=company_name)
            except Company.DoesNotExist:
                try:
                    companies = Company.objects.filter(slug__constains=company_name)
                except Company.DoesNotExist:
                   raise CommandError('Company "%s" does not exist' % company_name)

            print 'Found %d ocurrences with keyword "%s"' % (len(companies), company_name)
            for company in companies:
                print 'Name:', company.name
                print 'Date:', company.date_creation
                print 'Active:', company.is_active
                print

            self.stdout.write('Successful operation!')
