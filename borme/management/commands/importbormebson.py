# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from borme.models import Company, Borme, Acto, Person, Cargo, Config
from mongoengine.errors import ValidationError, NotUniqueError

import bson
import os
import re
import time
from datetime import datetime

from borme_parser import CARGOS_KEYWORD

RE_CARGOS_KEYWORD = '(%s)' % '|'.join(CARGOS_KEYWORD)
RE_CARGOS_KEYWORD_NG = '(?:\.\s*%s|$)' % '|'.join(RE_CARGOS_KEYWORD)  # FIXME:MAL pero funciona RE_...

regex1 = re.compile(RE_CARGOS_KEYWORD + ':\s+(.*?)' + RE_CARGOS_KEYWORD_NG)


class Command(BaseCommand):
    args = '<bson files, ...>'
    help = 'Import BSON parsed BORME'

    def handle(self, *args, **options):
        start_time = time.time()

        for filename in args:
            pdf_name = os.path.basename(filename).split('.pdf')[0]
            print
            print pdf_name

            fp = open(filename, 'rb')
            bs = fp.read()
            docs = bson.decode_all(bs)
            try:
                borme = Borme.objects.get(name=pdf_name)
            except Borme.DoesNotExist:
                print 'Creando borme', pdf_name

                borme = Borme(name=pdf_name)
                borme.save()

            # TODO: borrar si hubieran actos para este borme?
            for doc in docs:
                try:
                    #print "Importando acto con id", doc['ID']
                    #print doc

                    #company = Company.objects.get_or_create(name=doc['Nombre'])
                    #if not Company.objects.exists(name=doc['Nombre']):
                    company_name = doc['Nombre'].encode('utf-8')
                    try:
                        company = Company.objects.get(name=doc['Nombre'])
                    except Company.DoesNotExist:
                        print 'Creando empresa', company_name, type(company_name)
                        company = Company()
                        company.name = doc['Nombre']
                    company.in_bormes = [pdf_name]
                    company.in_bormes.append(pdf_name)
                    company.in_bormes = list(set(company.in_bormes))
                    try:
                        company.save()
                    except NotUniqueError, e:
                        print 'ERROR creando empresa:', company_name
                        print e
                        continue

                    try:
                        acto = Acto.objects.get(borme=borme.name, id_acto=doc['ID'])
                    except Acto.DoesNotExist:
                        print 'Creando acto:', doc['ID'], company_name
                        acto = Acto(company=company.slug, borme=borme.name, id_acto=doc['ID'])

                    for k, v in doc.iteritems():
                        k = k.encode('utf-8')
                        v = v.encode('utf-8')
                        print k, v
                        if k in ('Revocaciones', 'Reelecciones', 'Cancelaciones de oficio de nombramientos', 'Nombramientos'):
                            for match in regex1.finditer(v):
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

                                    p.in_companies.append(company.slug)
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
                            acto.__setattr__(k, v)

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
