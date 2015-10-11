# -*- coding: utf-8 -*-

from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError

from mongoengine import *
from django_mongoengine.utils.module import Document
from bormeparser.regex import SOCIEDADES as SOCIEDADES_DICT

#from borme_parser import DICT_KEYWORDS
DICT_KEYWORDS = {}  # FIXME
SOCIEDADES = tuple(SOCIEDADES_DICT.items())

# TODO: i18n 2o valor
PROVINCES = (
    ('Malaga', 'Málaga'),
    ('Sevilla', 'Sevilla'),
    ('Granada', 'Granada'),
)


class CargoCompany(EmbeddedDocument):
    title = StringField()
    name = ReferenceField('Company')
    date_from = DateTimeField()
    date_to = DateTimeField()

    def __str__(self):
        d_from = ''
        d_to = ''
        if self.date_from:
            d_from = 'From: %s' % self.date_from.strftime('%x')
        if self.date_to:
            d_to = 'To: %s' % self.date_to.strftime('%x')
        return '%s: %s (%s %s)' % (self.title, self.name, d_from, d_to)


# TODO: subclass CargoCompany
class CargoPerson(EmbeddedDocument):
    title = StringField()
    name = ReferenceField('Person')
    date_from = DateTimeField()
    date_to = DateTimeField()

    def __str__(self):
        d_from = ''
        d_to = ''
        if self.date_from:
            d_from = 'From: %s' % self.date_from.strftime('%x')
        if self.date_to:
            d_to = 'To: %s' % self.date_to.strftime('%x')
        return '%s: %s (%s %s)' % (self.title, self.name, d_from, d_to)


class Borme(Document):
    """ Edicion de BORME """
    cve = StringField(max_length=30)
    date = DateTimeField()
    year = IntField()
    url = URLField()
    #url = StringField(max_length=100)
    type = StringField(max_length=1)
    from_reg = IntField()
    until_reg = IntField()
    from_page = IntField()
    until_page = IntField()
    #province = StringField(max_length=100, choices=PROVINCES)
    province = StringField(max_length=100)
    section = StringField(max_length=20)
    pages = IntField()
    anuncios = ListField(IntField())

    def get_absolute_url(self):
        return reverse('borme-borme', args=[str(self.cve)])

    def __str__(self):
        return self.cve


class Person(Document):
    """ Persona """
    name = StringField(max_length=200)
    slug = StringField(unique=True)
    in_companies = ListField(ReferenceField('Company'))
    in_bormes = ListField(ReferenceField('Borme'))

    cargos_actuales = ListField(EmbeddedDocumentField('CargoCompany'))
    cargos_historial = ListField(EmbeddedDocumentField('CargoCompany'))

    # last access
    # number of visits

    def update_cargos_entrantes(self, cargos):
        """ cargos = [CargoCompany] """

        self.cargos_actuales.extend(cargos)
        #for cargo in cargos:
        #    self.cargos_actuales_c.append(cargo)

    def update_cargos_salientes(self, cargos):
        """ cargos = [CargoCompany] """

        for cargo in cargos:
            if cargo in self.cargos_actuales:
                self.cargos_actuales.remove(cargo)
            self.cargos_historial.append(cargo)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Person, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('borme-persona', args=[str(self.slug)])

    def __str__(self):
        return self.name


class Company(Document):
    """ Sociedad """
    name = StringField(max_length=250)
    nif = StringField(max_length=10)
    slug = StringField(unique=True)
    date_creation = DateTimeField()
    is_active = BooleanField(default=False)
    type = StringField(choices=SOCIEDADES)

    in_bormes = ListField(ReferenceField('Borme'))
    anuncios = ListField(IntField())

    cargos_actuales_p = ListField(EmbeddedDocumentField('CargoPerson'))
    cargos_actuales_c = ListField(EmbeddedDocumentField('CargoCompany'))
    cargos_historial_p = ListField(EmbeddedDocumentField('CargoPerson'))
    cargos_historial_c = ListField(EmbeddedDocumentField('CargoCompany'))

    @property
    def cargos_actuales(self):
        return self.cargos_actuales_p + self.cargos_actuales_c

    @property
    def cargos_historial(self):
        return self.cargos_historial_p + self.cargos_historial_c

    # last access
    # number of visits

    def save(self, *args, **kwargs):
        # TODO: Cambiar SOCIEDAD LIMITADA por SL, SOCIEDAD ANONIMA por SA, COOP, SCL...
        #if self.name.endswith('SOCIEDAD LIMITADA'):
            #...

        self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)

    def update_cargos_entrantes(self, cargos):
        """ cargos = [CargoCompany/CargoPerson] """

        for cargo in cargos:
            if isinstance(cargo, CargoCompany):
                self.cargos_actuales_c.append(cargo)
            elif isinstance(cargo, CargoPerson):
                self.cargos_actuales_p.append(cargo)
        #self.cargos_actuales_p.extend(cargos)

    def update_cargos_salientes(self, cargos):
        """ cargos = [CargoCompany/CargoPerson] """

        for cargo in cargos:
            if isinstance(cargo, CargoCompany):
                if cargo in self.cargos_actuales_c:
                    self.cargos_actuales_c.remove(cargo)
                self.cargos_historial_c.append(cargo)
            elif isinstance(cargo, CargoPerson):
                if cargo in self.cargos_actuales_p:
                    self.cargos_actuales_p.remove(cargo)
                self.cargos_historial_p.append(cargo)

    def get_absolute_url(self):
        return reverse('borme-empresa', args=[str(self.slug)])

    def __str__(self):
        return self.name


class Anuncio(Document):
    id_anuncio = IntField()
    borme = ReferenceField('Borme')
    company = ReferenceField('Company')
    datos_registrales = StringField()
    actos = DictField()

    def get_absolute_url(self):
        return reverse('borme-anuncio', args=[str(self.id_anuncio)])

    def __str__(self):
        return '%d (%d actos)' % (self.id_anuncio, len(self.actos.keys()))


class Config(Document):
    last_modified = DateTimeField()
    version = StringField()


class BormeLog(Document):
    date_created = DateTimeField()
    date_updated = DateTimeField()
    date_parsed = DateTimeField()
    borme_cve = StringField(max_length=30)
    parsed = BooleanField(default=False)
    errors = IntField(default=0)
    path = StringField()
