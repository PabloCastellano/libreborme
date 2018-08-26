from borme.models import Company, Person
from borme.utils.strings import slug2


def extinguir_sociedad(company, date):
    """Marca en la BD una sociedad como extinguida.

    Se llama a esta función cuando una sociedad se extingue.
    Todos los cargos vigentes pasan a la lista de cargos cesados (historial).
    Modifica los modelos Company y Person.
    company: Company object

    :param date: Fecha de la extinción
    :type date: datetime.date
    """
    company.date_extinction = date
    company.date_updated = date
    company.status = 'inactive'

    for cargo in company.cargos_actuales_c:
        cargo['date_to'] = date.isoformat()
        company.cargos_historial_c.append(cargo)
        c_cesada = Company.objects.get(slug=slug2(cargo['name']))
        c_cesada._cesar_cargo(company.fullname, date.isoformat())
        c_cesada.save()

    for cargo in company.cargos_actuales_p:
        cargo['date_to'] = date.isoformat()
        company.cargos_historial_p.append(cargo)
        p_cesada = Person.objects.get(slug=slug2(cargo['name']))
        p_cesada._cesar_cargo(company.fullname, date.isoformat())
        p_cesada.save()

    company.cargos_actuales_c = []
    company.cargos_actuales_p = []
    company.save()
