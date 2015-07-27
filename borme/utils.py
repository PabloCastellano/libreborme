from .models import Company, Borme, Anuncio, Person, Cargo
from mongoengine.errors import ValidationError, NotUniqueError

import bormeparser
from bormeparser import regex


def import_borme_file(filename):
    """
    Import BORME to MongoDB database


def _import1(borme):
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0}
    try:
        nuevo_borme = Borme.objects.get(cve=borme.cve)
    except Borme.DoesNotExist:
        print('Creando borme %s' % borme.cve)
        results['created_bormes'] += 1
        nuevo_borme = Borme(cve=borme.cve, date=borme.date, url=borme.url, province=borme.provincia, section=borme.seccion).save()

    # TODO: borrar si hubieran actos para este borme?
    for n, anuncio in enumerate(borme.get_anuncios(), 1):
        try:
            print('%d: Importando anuncio: %s' % (n, anuncio))
            #company = Company.objects.get_or_create(name=acto.empresa)
            #if not Company.objects.exists(name=acto.empresa):
            try:
                company = Company.objects.get(name=anuncio.empresa)
            except Company.DoesNotExist:
                print('Creando empresa %s' % anuncio.empresa)
                results['created_companies'] += 1
                company = Company(name=anuncio.empresa)
            company.in_bormes.append(nuevo_borme)
            try:
                company.save()
            except NotUniqueError as e:
                print('ERROR creando empresa: %s' % anuncio.empresa)
                print(e)
                continue

            try:
                nuevo_anuncio = Anuncio.objects.get(borme=nuevo_borme, id_anuncio=anuncio.id)
            except Anuncio.DoesNotExist:
                print('Creando anuncio %d %s:' % (anuncio.id, anuncio.empresa))
                nuevo_anuncio = Anuncio(company=company, borme=nuevo_borme, id_anuncio=anuncio.id)
                results['created_anuncios'] += 1

            actos = anuncio.get_actos()
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
                                    results['created_companies'] += 1
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
                                    results['created_persons'] += 1
                                    p = Person(name=nombre)

                                p.in_companies.append(company)
                                p.in_bormes.append(nuevo_borme)
                                try:
                                    p.save()
                                except NotUniqueError as e:
                                    print('ERROR creando persona: %s' % nombre)
                                    print(e)

                        kk = k.replace('.', '||')
                        nuevo_anuncio.actos[kk] = l

                else:
                    # FIXME:
                    # mongoengine.errors.ValidationError: ValidationError (Anuncio:55b37c97cf28dd2cfa8d069e) (Invalid diction
                    # ary key name - keys may not contain "." or "$" characters: ['actos'])
                    kk = k.replace('.', '||')
                    nuevo_anuncio.actos[kk] = v

            nuevo_anuncio.save()
            company.anuncios.append(nuevo_anuncio)
            company.save()
            nuevo_borme.anuncios.append(nuevo_anuncio)
            nuevo_borme.save()

        except ValidationError as e:
            print('ERROR importing borme')
            print(e)

def print_results(results, borme):
    print()
    print('BORMEs creados: %d' % results['created_bormes'])
    print('Anuncios creados: %d/%d' % (results['created_anuncios'], len(borme.get_anuncios())))
    print('Empresas creadas: %d' % results['created_companies'])
    print('Personas creadas: %d' % results['created_persons'])
    return True
