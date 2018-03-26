from django.core.management.base import BaseCommand
from borme.models import get_borme_urls_from_slug


class Command(BaseCommand):
    help = 'Show the sources where the information about some entity was retrieved'

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str, help="person or company slug")

    def handle(self, *args, **options):

        urls = get_borme_urls_from_slug(options["slug"])

        if len(urls) == 0:
            print('Not found')
            return

        for url in urls:
            print(url)
