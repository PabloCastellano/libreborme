# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from borme.models import Company, Borme, Acto, Person, Cargo, Config
from mongoengine.errors import ValidationError, NotUniqueError

import csv
import os
import re
import time
from datetime import datetime

from borme_parser import ALL_KEYWORDS, CARGOS_KEYWORD

RE_CARGOS_KEYWORD = '(%s)' % '|'.join(CARGOS_KEYWORD)
RE_CARGOS_KEYWORD_NG = '(?:\.\s*%s|$)' % '|'.join(RE_CARGOS_KEYWORD)  # FIXME:MAL pero funciona RE_...

regex1 = re.compile(RE_CARGOS_KEYWORD + ':\s+(.*?)' + RE_CARGOS_KEYWORD_NG)


class Command(BaseCommand):
    args = '<csv files, ...>'
    help = 'Import CSV parsed BORME'

    def handle(self, *args, **options):
        start_time = time.time()

        for filename in args:
            pdf_name = os.path.basename(filename).split('.pdf')[0]
            print
            print pdf_name

            fp = open(filename)
            csvr = csv.DictReader(fp)
            try:
                borme = Borme.objects.get(name=pdf_name)
            except Borme.DoesNotExist:
                print 'Creando borme', pdf_name

                borme = Borme(name=pdf_name)
                borme.save()

            # TODO: borrar si hubieran actos para este borme?
            for row in csvr:
                try:
                    #print "Importando acto con id", row['ID']
                    #print row

                    #company = Company.objects.get_or_create(name=row['Nombre'])
                    #if not Company.objects.exists(name=row['Nombre']):
                    try:
                        company = Company.objects.get(name=row['Nombre'])
                    except Company.DoesNotExist:
                        print 'Creando empresa', row['Nombre']
                        company = Company()
                        company.name = unicode(row['Nombre'], 'utf-8')
                    company.in_bormes = [pdf_name]
                    company.in_bormes.append(pdf_name)
                    company.in_bormes = list(set(company.in_bormes))
                    try:
                        company.save()
                    except NotUniqueError, e:
                        print 'ERROR creando empresa:', row['Nombre']
                        print e
                        continue

                    try:
                        acto = Acto.objects.get(borme=borme.name, id_acto=row['ID'])
                    except Acto.DoesNotExist:
                        #print 'Creando acto:', row['ID'], row['Nombre']
                        acto = Acto(company={"name": company.name, "slug": company.slug}, borme=borme.name, id_acto=row['ID'])

                    for k in ALL_KEYWORDS:
                        if row[k] not in (None, ''):
                            if k in ('Revocaciones', 'Reelecciones', 'Cancelaciones de oficio de nombramientos', 'Nombramientos'):
                                print k, row[k]
                                for match in regex1.finditer(row[k]):
                                    cargo, nombres = match.group(1), match.group(2)
                                    print cargo, nombres
                                    l = []
                                    for nombre in nombres.split(';'):
                                        print '  ', nombre
                                        l.append(Cargo(titulo=match.group(1), nombre=nombre))

                                        try:
                                            p = Person.objects.get(name=nombre)
                                        except Person.DoesNotExist:
                                            print 'Creando persona:', nombre
                                            p = Person(name=nombre)

                                        p.in_companies.append({"name": company.name, "slug": company.slug})
                                        p.in_companies = list(set(p.in_companies))
                                        p.in_bormes.append(pdf_name)
                                        p.in_bormes = list(set(p.in_bormes))
                                        try:
                                            p.save()
                                        except NotUniqueError, e:
                                            print 'ERROR creando persona:', nombre
                                            print e
                                    acto.__setattr__(k, l)

                            else:
                                acto.__setattr__(k, row[k])

                    acto.save()

                except ValidationError, e:
                    print e

            fp.close()

        config = Config.objects.first()
        if config:
            config.last_modified = datetime.today()
        else:
            config = Config(last_modified=datetime.today())
        config.save()

        # Elapsed time
        elapsed_time = time.time() - start_time
        print '\nElapsed time: %.2f seconds' % elapsed_time
