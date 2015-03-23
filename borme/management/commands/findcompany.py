from django.core.management.base import BaseCommand, CommandError
from borme.models import Company

class Command(BaseCommand):
    args = '<company name or slug ...>'
    help = 'Find a company and show its information'

    def handle(self, *args, **options):
        for company_name in args:

            companies = Company.objects.filter(name__icontains=company_name)
            if not companies:
                companies = Company.objects.filter(slug__contains=company_name)

            for company in companies:
                print 'Name:', company.name
                print 'Slug:', company.slug
                print 'Date:', company.date_creation
                print 'Active:', company.is_active
                print

            print 'Found %d ocurrences with keyword "%s"' % (len(companies), company_name)
            print
