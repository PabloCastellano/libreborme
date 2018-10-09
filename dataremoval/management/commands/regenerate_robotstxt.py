from django.core.management.base import BaseCommand

from dataremoval.utils import regenerate_robotstxt


class Command(BaseCommand):
    help = 'Regenerate robots.txt file'

    def handle(self, *args, **options):
        print_output = int(options['verbosity']) > 1

        results = regenerate_robotstxt(print_output)
        print("Written {path} ({companies} companies and {persons} persons)"
              .format(**results))
