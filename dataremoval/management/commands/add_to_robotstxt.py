from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from borme.models import Company, Person
from dataremoval.models import CompanyRobotsTxt, PersonRobotsTxt
from dataremoval.utils import regenerate_robotstxt


class Command(BaseCommand):
    help = 'Add to robots.txt'

    def add_arguments(self, parser):
        parser.add_argument("-n", "--do-not-regenerate",
                            action='store_true',
                            default=False,
                            help="Add to DB but do not regenerate robots.txt")
        parser.add_argument("slug", type=str, help="person or company slug")

    def handle(self, *args, **options):
        slug = options["slug"]
        try:
            entity = Person.objects.get(slug=slug)
            robotstxt = PersonRobotsTxt(person=entity)
            robotstxt.save()
            print("Added person: {}".format(entity.name))
        except Person.DoesNotExist:
            try:
                entity = Company.objects.get(slug=slug)
                robotstxt = CompanyRobotsTxt(company=entity)
                robotstxt.save()
                print("Added company: {}".format(entity.name))
            except Company.DoesNotExist:
                print('Not found')
                return
        except IntegrityError:
                print('{} is already included'.format(slug))
                return

        if not options["do_not_regenerate"]:
            print_output = int(options['verbosity']) > 1
            results = regenerate_robotstxt(print_output)
            print("Written {path} ({companies} companies and {persons} persons)"
                  .format(**results))
