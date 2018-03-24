from django.core.management.base import BaseCommand

from borme.importer import psql_update_documents


class Command(BaseCommand):
    help = 'Update FTS PostgreSQL document fields'

    def handle(self, *args, **options):
        affected_rows = psql_update_documents()
        print("{} records were updated".format(affected_rows))
