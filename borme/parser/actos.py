from borme.models import Company, Person
from borme.utils.strings import slug2


ACTOS_ENTRANTES = ["Nombramientos", "Reelecciones"]
ACTOS_SALIENTES = ["Revocaciones", "Cancelaciones de oficio de nombramientos",
                   "Ceses/Dimisiones", "Modificación de poderes"]
ACTOS_CARGOS = ACTOS_ENTRANTES + ACTOS_SALIENTES
ACTOS_CREACION = ["Constitución"]
ACTOS_EXTINCION = ["Extinción"]


def is_acto_reapertura_hoja_registral(acto):
    """Comprueba si es un acto de reapertura de hoja registral

    Engloba los actos siguientes:
    Reapertura hoja registral
    Articulo 378.5 del Reglamento del Registro Mercantil

    :param acto: Nombre del acto mercantil
    :type acto: str
    :rtype: bool
    """
    return acto in ["Reapertura hoja registral",
                    "Articulo 378.5 del Reglamento del Registro Mercantil"]


def is_acto_cierre_hoja_registral(acto):
    """Comprueba si es un acto de cierre de hoja registral

    Engloba los actos siguientes:
    Cierre provisional hoja registral por baja en el índice de Entidades Jurídicas
    Cierre provisional hoja registral por revocación del NIFde Entidades Jurídicas
    Cierre provisional hoja registral art. 137.2 Ley 43/1995 Impuesto de Sociedades
    Cierre provisional de la hoja registral por revocación del NIF

    :param acto: Nombre del acto mercantil
    :type acto: str
    :rtype: bool
    """
    return acto.startswith("Cierre provisional")


def activar_sociedad(company, date):
    """Marca en la BD una sociedad como activa (Reapertura hoja registral).

    Se llama a esta función cuando se reabre la hoja registral de una sociedad.
    No se alteran los cargos vigentes.
    Modifica el modelo Company

    :param company: Compañía que se reabre hoja registral
    :type company: Company object
    :param date: Fecha de la reapertura
    :type date: datetime.date
    """
    company.date_updated = date
    company.status = 'active'
    company.save()


def suspender_sociedad(company, date):
    """Marca en la BD una sociedad como suspendida (Cierre hoja registral).

    Se llama a esta función cuando se cierra la hoja registral de una sociedad.
    No se alteran los cargos vigentes.
    Modifica el modelo Company

    :param company: Compañía que se cierra hoja registral
    :type company: Company object
    :param date: Fecha de la suspensión
    :type date: datetime.date
    """
    company.date_updated = date
    company.status = 'suspended'
    company.save()


def _resign_positions(company, date):
    """ Marca todos los cargos de una empresa como finalizados
    """
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


def disolver_sociedad(company, date, reason):
    """Marca en la BD una sociedad como disuelta.

    Se llama a esta función cuando una sociedad se disuelve.
    Todos los cargos vigentes pasan a la lista de cargos cesados (historial).
    Modifica los modelos Company y Person.
    company: Company object

    :param company: Compañía que se disuelve
    :type company: Company object
    :param date: Fecha de la extinción
    :type date: datetime.date
    """
    company.date_updated = date
    company.date_dissolution = date
    company.reason_dissolution = reason
    company.status = 'dissolved'

    # No debería ser necesario pero así nos aseguramos de que no queda
    # ningún cargo activo
    # TODO: Solo dejar los liquidadores
    _resign_positions(company, date)
    company.save()


def extinguir_sociedad(company, date):
    """Marca en la BD una sociedad como extinguida.

    Se llama a esta función cuando una sociedad se extingue.
    Todos los cargos vigentes pasan a la lista de cargos cesados (historial).
    Modifica los modelos Company y Person.
    company: Company object

    :param company: Compañía que se extingue
    :type company: Company object
    :param date: Fecha de la extinción
    :type date: datetime.date
    """
    company.date_updated = date
    company.date_extinction = date
    company.status = 'inactive'
    _resign_positions(company, date)
    company.save()
