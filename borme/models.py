# -*- coding: utf-8 -*-

from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError

from mongoengine import *
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
    anuncios = ListField(ReferenceField('Anuncio'))

    def __str__(self):
        return self.cve


class Person(Document):
    """ Persona """
    name = StringField(max_length=200)
    slug = StringField(unique=True)
    in_companies = ListField(ReferenceField('Company'))
    in_bormes = ListField(ReferenceField('Borme'))

    # last access
    # number of visits

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Person, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('borme-persona', args=[str(self.slug)])

    def __str__(self):
        return self.name


class Company(Document):
    """ Sociedad """
    name = StringField(max_length=200)
    nif = StringField(max_length=10)
    slug = StringField(unique=True)
    date_creation = DateTimeField()
    is_active = BooleanField(default=False)
    type = StringField(choices=SOCIEDADES)

    in_bormes = ListField(ReferenceField('Borme'))
    anuncios = ListField(ReferenceField('Anuncio'))

    # last access
    # number of visits

    def save(self, *args, **kwargs):
        # TODO: Cambiar SOCIEDAD LIMITADA por SL, SOCIEDAD ANONIMA por SA, COOP, SCL...
        #if self.name.endswith('SOCIEDAD LIMITADA'):
            #...

        self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('borme-empresa', args=[str(self.slug)])

    def __str__(self):
        return self.name


class CargoCompany(EmbeddedDocument):
    titulo = StringField()
    nombre = ReferenceField('Company')

    def __str__(self):
        return '%s: %s' % (self.titulo, self.nombre)


class CargoPerson(EmbeddedDocument):
    titulo = StringField()
    nombre = ReferenceField('Person')

    def __str__(self):
        return '%s: %s' % (self.titulo, self.nombre)


class Anuncio(Document):
    id_anuncio = IntField()
    borme = ReferenceField('Borme')
    company = ReferenceField('Company')
    datos_registrales = StringField()
    actos = DictField()

    def __str__(self):
        return '%d (%d actos)' % (self.id_anuncio, len(self.actos.keys()))


class Config(Document):
    last_modified = DateTimeField()
    version = StringField()
