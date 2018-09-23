from borme.parser import actos
#
# All backends must inherit from these classes and implement
# the following two methods:
#
# BormeBase:
#   from_json(cls, filename):
#   _set_anuncios(self, anuncios):
#   get_anuncios(self):
#   __lt__(self, other):
#
# BormeAnuncioBase:
#   __init__(self, anuncio)
#
# BormeActoBase:
#   __init__(self, acto)
#   @property value(self)


class BormeActoBase(object):

    def __init__(self):
        self.name = None

    def is_acto_cargo(self):
        """Comprueba si el acto mercantil contiene nombres de cargos"""
        return self.name in actos.ACTOS_CARGOS

    def is_acto_cargo_entrante(self):
        """Comprueba si el acto nombra nuevos cargos """
        return self.name in actos.ACTOS_ENTRANTES

    def is_acto_cargo_saliente(self):
        """Comprueba si el acto cesa cargos anteriores """
        return self.name in actos.ACTOS_SALIENTES

    def __repr__(self):
        return "BormeActo({})".format(self.name)


class BormeAnuncioBase(object):
    """Representa un anuncio con un conjunto de actos mercantiles
       (Constitucion, Nombramientos, ...)
    """

    # def __init__(self, id, empresa, actos, extra, datos_registrales=None):
    def __init__(self):
        self.id = None
        self.empresa = None
        self.registro = None
        self.sucursal = None
        self.liquidacion = None
        self.datos_registrales = None
        self.actos = []

    def get_borme_actos(self):
        return self.actos

    def get_actos(self):
        for acto in self.actos:
            yield acto.name, acto.value

    def __repr__(self):
        return "<BormeAnuncio({}) {} (r:{}, s:{}, l:{}) ({})>".format(
                    self.id, self.empresa, self.registro, self.sucursal,
                    self.liquidacion, len(self.actos))


class BormeBase(object):

    def __init__(self, date, seccion, provincia, num, cve, anuncios=None,
                 url=None):
        """
            :param date: Fecha de publicación
            :type date: datetime.date
            :param seccion: Sección del BORME
            :type seccion: str
            :param provincia: Provincia del BORME
            :type provincia: str
            :param num: Número de BORME
            :type num: int
            :param cve: CVE del BORME
            :type cve: int
            :param anuncios: Anuncios
            :type anuncios: ??? FIXME
            :param url: URL de descarga del BORME
            :type url: str
        """
        self.date = date
        self.seccion = seccion
        self.provincia = provincia
        self.num = num
        self.cve = cve
        self.anuncios = {}
        self._set_anuncios(anuncios)
        self.anuncios_rango = (min(self.anuncios.keys()),
                               max(self.anuncios.keys()))
        self.url = url

    @classmethod
    def from_json(cls, filename):
        """Crea una instancia Borme a partir de un BORME-JSON.

        El parámetro filename puede ser la ruta a un archivo o un objeto file
        de un fichero JSON ya abierto.
        """
        raise NotImplementedError

    def _set_anuncios(self, anuncios):
        """
            anuncios: [BormeAnuncio]
        """
        raise NotImplementedError

    def get_anuncios(self):
        """
        [BormeAnuncio]
        """
        return list(self.anuncios.values())

    def __lt__(self, other):
        return self.anuncios_rango[1] < other.anuncios_rango[0]

    def __repr__(self):
        return "<Borme({}) seccion:{} provincia:{}>".format(
                    self.date, self.seccion, self.provincia)
