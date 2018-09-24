from django.core.management.base import BaseCommand
from django.db import connection
from borme.models import Anuncio, Company, Person
from borme.parser.actos import is_acto_cargo
from borme.utils.strings import convertir_iniciales
from borme.templatetags.utils import slug2

from datetime import datetime


def new_slug(old_slug):
    number = datetime.now().strftime('%s')
    slug = '{}-{}'.format(old_slug.replace(' ', '').replace('.', '-'), number)
    return slug


class Command(BaseCommand):
    help = 'Hide some person'

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str, help="person or company slug")

    def handle(self, *args, **options):

        try:
            entity = Person.objects.get(slug=options["slug"])
        except Person.DoesNotExist:
            print('Not found')
            return

        companies = []
        iniciales = convertir_iniciales(entity.name)
        nuevo_slug = new_slug(iniciales)

        # Remove name from company positions
        for company_name in entity.in_companies:
            c = Company.objects.get(slug=slug2(company_name))
            cargos = c.cargos_actuales_p.copy()
            for p in cargos:
                if p['name'] == entity.name:
                    p['name'] = iniciales
                    p['slug'] = nuevo_slug
                    companies.append(c.slug)
            c.cargos_actuales_p = cargos
            cargos = c.cargos_historial_p.copy()
            for p in cargos:
                if p['name'] == entity.name:
                    p['name'] = iniciales
                    p['slug'] = nuevo_slug
                    companies.append(c.slug)
            c.cargos_historial_p = cargos
            c.save()

        # Remove name from anuncios in companies
        for c_slug in companies:
            for anuncio in Anuncio.objects.filter(company=c_slug):
                actos = anuncio.actos.copy()
                for k, cargos in actos.items():
                    if is_acto_cargo(k):
                        for cargo in cargos:
                            if cargo['name'] == entity.name:
                                cargo['name'] = iniciales
                                cargo['slug'] = nuevo_slug
                anuncio.actos = actos
                anuncio.save()

        # Change slug which is primary key
        new_entity = Person()
        new_entity.name = iniciales
        new_entity.slug = nuevo_slug
        new_entity.in_companies = entity.in_companies
        new_entity.in_bormes = entity.in_bormes
        new_entity.date_updated = entity.date_updated
        new_entity.save()
        entity.delete()
        print('Done')
        print(new_entity.get_absolute_url())
        print()

        for query in connection.queries:
            print(query['sql'])
            print()

        # TODO: clear cache
