from .models import Company, Borme, Acto, Person, Cargo, EmbeddedCompany
from mongoengine.errors import ValidationError, NotUniqueError

import bormeparser


def import_borme_to_mongodb(filename):
    """
    Import BORME to MongoDB database

    :param filename:
    :return:
    """
    borme = bormeparser.parse(filename)

    try:
        Borme.objects.get(name=borme.cve)
    except Borme.DoesNotExist:
        print('Creando borme %s' % borme.cve)
        Borme(name=borme.cve).save()

    # TODO: borrar si hubieran actos para este borme?
    for acto in borme.get_actos():
        try:
            #print('Importando acto con id %s' % acto.id)
            #print(acto)

            #company = Company.objects.get_or_create(name=acto.empresa)
            #if not Company.objects.exists(name=acto.empresa):
            try:
                company = Company.objects.get(name=acto.empresa)
            except Company.DoesNotExist:
                print('Creando empresa %s' % acto.empresa)
                company = Company()
                company.name = acto.empresa
            company.in_bormes = {borme.cve}
            company.in_bormes.add(borme.cve)
            try:
                company.save()
            except NotUniqueError as e:
                print('ERROR creando empresa: %s' % acto.empresa)
                print(e)
                continue

            try:
                acto = Acto.objects.get(borme=borme.cve, id_acto=acto.id)
            except Acto.DoesNotExist:
                print('Creando acto %d %s:' % (acto.id, acto.empresa))
                acto = Acto(company={"name": company.name, "slug": company.slug}, borme=borme.cve, id_acto=acto.id)

            for k, v in acto.get_actos():
                print(k, v)
                if k in ('Revocaciones', 'Reelecciones', 'Cancelaciones de oficio de nombramientos', 'Nombramientos'):
                    for cargo, nombres in v:
                        print(cargo, nombres)
                        l = []
                        for nombre in nombres:
                            print('  %s' % nombre)
                            l.append(Cargo(titulo=cargo, nombre=nombre))

                            try:
                                p = Person.objects.get(name=nombre)
                            except Person.DoesNotExist:
                                print('Creando persona: %s' % nombre)
                                p = Person(name=nombre)

                            p.in_companies.append(EmbeddedCompany(name=company.name, slug=company.slug))
                            p.in_companies = [dict(t) for t in set([tuple(eval(d.to_json()).items()) for d in p.in_companies])]
                            p.in_bormes.append(borme.cve)
                            p.in_bormes = list(set(p.in_bormes))
                            try:
                                p.save()
                            except NotUniqueError as e:
                                print('ERROR creando persona: %s' % nombre)
                                print(e)
                        acto.__setattr__(k, l)

                else:
                    acto.__setattr__(k, v)

            acto.save()

        except ValidationError as e:
            print(e)

    return True
