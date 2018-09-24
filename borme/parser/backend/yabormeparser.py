import io
import json
import logging

from datetime import datetime

from borme.parser.backend.base import (
        BormeAnuncioBase, BormeActoBase, BormeBase
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class BormeActo(BormeActoBase):

    def __init__(self, acto, fecha):
        """
        :param acto:
        :type acto: dictionary
        :param fecha: Fecha que aparece en Datos Registrales
        :type fecha: `datetime.date`
        """
        super().__init__()
        self.name = acto['label']
        del acto['label']
        self._acto = acto
        self.fecha = fecha

    @property
    def roles(self):
        """Devuelve cargos en formato diccionario

        {"Apoderado": ['pepito', 'juanito'], "Adm.Unico": "joan"}
        """
        if not self.is_acto_cargo():
            raise RuntimeError("This is not a Borme with roles")

        roles = {}
        for role, name in self._acto['roles']:
            roles.setdefault(role, [])
            roles[role].append(name)
        return roles

    def __getattr__(self, key):
        if key in self._acto:
            return self._acto[key]
        else:
            logger.warn("No such attribute: " + key)
            return None


class BormeAnuncio(BormeAnuncioBase):

    def __init__(self, anuncio):
        super().__init__()
        self.id = anuncio["code"]
        self.empresa = anuncio["company"]
        self.registro = anuncio["register"]
        self.sucursal = anuncio["branch"]

        self._set_datos_registrales(anuncio['announcements'])

        for acto in anuncio["announcements"]:
            # Do not treat Datos Registrales as acto
            if acto['label'] == 'Datos registrales':
                continue

            borme_acto = BormeActo(acto, self.fecha)
            self.actos.append(borme_acto)

    def _set_datos_registrales(self, announcements):
        for acto in announcements:
            if acto['label'] == 'Datos registrales':
                self.datos_registrales = acto['datos_registrales']
                fecha = datetime.strptime(acto['fecha'], '%Y-%m-%d')
                self.fecha = fecha.date()
                return


class Borme(BormeBase):
    """yabormeparser Borme implementation"""

    VERSION_REQUIRED = "9001"

    @classmethod
    def from_json(cls, filename):

        if isinstance(filename, io.IOBase):
            content = filename.read().decode('utf-8')
            document = json.loads(content)
        else:
            with open(filename) as fp:
                document = json.load(fp)

        version = document['version']
        min_version = cls.VERSION_REQUIRED
        if version < min_version:
            logger.error("Yabormeparser version required is {}, found is {}"
                         .format(min_version, version))
            raise NotImplementedError

        cve = document['cve']
        publish_date = datetime.strptime(document['publish_date'], '%Y-%m-%d')
        publish_date = publish_date.date()
        seccion = document['seccion']
        provincia = document['provincia']
        num = document['num']
        url = None  # TODO: Url is not supported in yabormeparser

        announcements = []
        for page in document['pages']:
            announcements.extend(page)

        borme = Borme(publish_date, seccion, provincia, num, cve,
                      announcements, url)
        return borme

    def _set_anuncios(self, anuncios):
        self.anuncios = {}
        for anuncio in anuncios:
            id_ = anuncio["code"]
            self.anuncios[id_] = BormeAnuncio(anuncio)
