from .models import Company, Borme, Acto, Person, Cargo, EmbeddedCompany
from mongoengine.errors import ValidationError, NotUniqueError

import bormeparser
from bormeparser import regex


def import_borme_file(filename):
    """
    Import BORME to MongoDB database

    :param filename:
    :return:
    """
    created_actos = 0
    created_bormes = 0
    created_companies = 0
    created_persons = 0
    borme = bormeparser.parse(filename)

    try:
        Borme.objects.get(cve=borme.cve)
    except Borme.DoesNotExist:
        print('Creando borme %s' % borme.cve)
        created_bormes += 1
        Borme(cve=borme.cve, date=borme.date, url=borme.url, province=borme.provincia, section=borme.seccion).save()

    # TODO: borrar si hubieran actos para este borme?
    for n, acto in enumerate(borme.get_actos(), 1):
        try:
            print('%d: Importando acto: %s' % (n, acto))

            #company = Company.objects.get_or_create(name=acto.empresa)
            #if not Company.objects.exists(name=acto.empresa):
            try:
                company = Company.objects.get(name=acto.empresa)
            except Company.DoesNotExist:
                print('Creando empresa %s' % acto.empresa)
                created_companies += 1
                company = Company(name=acto.empresa)
            company.in_bormes = [borme.cve]
            #company.in_bormes.append(borme.cve)
            try:
                company.save()
            except NotUniqueError as e:
                print('ERROR creando empresa: %s' % acto.empresa)
                print(e)
                continue

            try:
                nuevo_acto = Acto.objects.get(borme=borme.cve, id_acto=acto.id)
            except Acto.DoesNotExist:
                print('Creando acto %d %s:' % (acto.id, acto.empresa))
                nuevo_acto = Acto(company={"name": company.name, "slug": company.slug}, borme=borme.cve, id_acto=acto.id)
                created_actos += 1

            actos = acto.get_actos()
            for k, v in actos.items():
                #print(k)
                #print(v)
                if k in ('Revocaciones', 'Reelecciones', 'Cancelaciones de oficio de nombramientos', 'Nombramientos'):
                    for cargo, nombres in v:
                        #print(cargo, nombres, len(nombres))
                        l = []
                        for nombre in nombres:
                            #print('  %s' % nombre)
                            l.append(Cargo(titulo=cargo, nombre=nombre))

                            if regex.is_company(nombre):
                                try:
                                    c = Company.objects.get(name=nombre)
                                except Company.DoesNotExist:
                                    print('Creando empresa: %s' % nombre)
                                    created_companies += 1
                                    c = Company(name=nombre)

                                # TODO: relations
                                try:
                                    c.save()
                                except NotUniqueError as e:
                                    print('ERROR creando empresa: %s' % nombre)
                                    print(e)

                            else:
                                try:
                                    p = Person.objects.get(name=nombre)
                                except Person.DoesNotExist:
                                    print('Creando persona: %s' % nombre)
                                    created_persons += 1
                                    p = Person(name=nombre)

                                p.in_companies.append(EmbeddedCompany(name=company.name, slug=company.slug))
                                #p.in_companies = [dict(t) for t in set([tuple(eval(d.to_json()).items()) for d in p.in_companies])]
                                p.in_bormes.append(borme.cve)
                                p.in_bormes = list(set(p.in_bormes))
                                try:
                                    p.save()
                                except NotUniqueError as e:
                                    print('ERROR creando persona: %s' % nombre)
                                    print(e)
                        nuevo_acto.__setattr__(k, l)

                else:
                    nuevo_acto.__setattr__(k, v)

            nuevo_acto.save()

        except ValidationError as e:
            print(e)

    print()
    print('BORMEs creados: %d' % created_bormes)
    print('Actos creados: %d/%d' % (created_actos, len(borme.get_actos())))
    print('Empresas creadas: %d' % created_companies)
    print('Personas creadas: %d' % created_persons)
    return True
