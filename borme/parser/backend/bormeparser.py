import io
import json
import logging
import re

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

    def __init__(self, name, value, fecha):
        """
        :param name: Nombre del acto
        :type name: str
        :param value: Texto del acto
        :type value: str
        :param fecha: Fecha que aparece en Datos Registrales
        :type fecha: `datetime.date`
        """
        super().__init__()
        self._acto = {name: value}
        self.name = name
        self._value = value
        self.fecha = fecha

    @property
    def value(self):
        if self.name == 'Disolución':
            return self._value
        raise ValueError('Cannot return value for acto: ' + name)

    @property
    def roles(self):
        """Devuelve cargos en formato diccionario

        {"Apoderado": ['pepito', 'juanito'], "Adm.Unico": "joan"}
        """
        if not self.is_acto_cargo():
            raise RuntimeError("This is not a Borme with roles")

        return self._value

    def __getattr__(self, key):
        return self._acto.get(key)


class BormeAnuncio(BormeAnuncioBase):

    def __init__(self, anuncio):
        super().__init__()
        self.id = anuncio[0]
        self.empresa = anuncio[1]["empresa"]
        self.registro = anuncio[1]["registro"]
        self.sucursal = anuncio[1]["sucursal"]
        self.liquidacion = anuncio[1]["liquidacion"]
        self.datos_registrales = anuncio[1]['datos registrales']

        self._set_datos_registrales(anuncio[1]['datos registrales'])

        for acto in anuncio[1]['actos']:
            for acto_nombre, valor in acto.items():
                # Do not treat Datos Registrales as acto
                if acto_nombre == 'Datos registrales':
                    self.datos_registrales = valor
                    continue

                borme_acto = BormeActo(acto_nombre, valor, self.fecha)
                self.actos.append(borme_acto)

    def _set_datos_registrales(self, datos_registrales):
        regexp = r'\(\s*\d{1,2}\.\d{2}\.\d{2}\)\.'
        self.datos_registrales = datos_registrales
        fecha = re.findall(regexp, datos_registrales)[0]
        self.fecha = datetime.strptime(fecha, '(%d.%m.%y).').date()


class Borme(BormeBase):
    """yabormeparser Borme implementation"""

    VERSION_REQUIRED = "2001"

    @classmethod
    def from_json(cls, filename):

        if isinstance(filename, io.IOBase):
            content = filename.read().decode('utf-8')
            document = json.loads(content)
        else:
            with open(filename) as fp:
                document = json.load(fp)

        version = document["version"]
        min_version = cls.VERSION_REQUIRED
        if version < min_version:
            logger.error("Yabormeparser version required is {}, found is {}"
                         .format(min_version, version))
            raise NotImplementedError

        cve = document['cve']
        publish_date = datetime.strptime(document['date'], '%Y-%m-%d')
        publish_date = publish_date.date()
        seccion = document['seccion']
        provincia = document['provincia']
        num = document['num']
        url = document.get('url')  # May be present or not

        announcements = document['anuncios']

        borme = Borme(publish_date, seccion, provincia, num, cve,
                      announcements, url)
        return borme

    def _set_anuncios(self, anuncios):
        announcements = sorted(anuncios.items(), key=lambda t: t[0])

        self.anuncios = {}
        for id_, anuncio in announcements:
            self.anuncios[id_] = BormeAnuncio((id_, anuncio))
