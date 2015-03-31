# -*- coding: utf-8 -*-

from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError

from mongoengine import *

from borme_parser import DICT_KEYWORDS

# TODO: i18n 2o valor
PROVINCES = (
    ('Malaga', 'Málaga'),
    ('Sevilla', 'Sevilla'),
    ('Granada', 'Granada'),
)


class Borme(Document):
    """ Edicion de BORME """
    filename = StringField(max_length=30)
    date = DateTimeField()
    type = StringField(max_length=1)
    from_reg = IntField()
    until_reg = IntField()
    from_page = IntField()
    until_page = IntField()
    province = StringField(max_length=100, choices=PROVINCES)
    pages = IntField()

    def __unicode__(self):
        return self.filename


# TEMP
class EmbeddedCompany(EmbeddedDocument):
    """ Sociedad embedded """
    name = StringField(max_length=200)
    slug = StringField()


class Person(Document):
    """ Persona """
    name = StringField(max_length=200)
    slug = StringField(unique=True)
    in_companies = ListField(StringField())
    in_companies2 = ListField(EmbeddedDocumentField(EmbeddedCompany))
    in_bormes = ListField(StringField())

    # last access
    # number of visits

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Person, self).save(*args, **kwargs)

    def get_absolute_url(self):
        #return reverse('borme.views.PersonView', args=[str(self.slug)])
        return '/persona/%s' % self.slug

    def __unicode__(self):
        return self.name


SOCIEDADES = (
    ('SA', 'Sociedad Anónima'),
    ('SL', 'Sociedad Limitada'),
    ('COOP', 'Cooperativa'),
)

class Company(Document):
    """ Sociedad """
    name = StringField(max_length=200)
    nif = StringField(max_length=10)
    slug = StringField(unique=True)
    date_creation = DateTimeField()
    is_active = BooleanField(default=False)
    type = StringField(choices=SOCIEDADES)

    in_bormes = ListField(StringField())

    # last access
    # number of visits

    def save(self, *args, **kwargs):
        # TODO: Cambiar SOCIEDAD LIMITADA por SL, SOCIEDAD ANONIMA por SA, COOP, SCL...
        #if self.name.endswith('SOCIEDAD LIMITADA'):
            #...

        self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)

    def get_absolute_url(self):
        #return reverse('borme.views.CompanyView', kwargs={slug: self.slug})
        return '/empresa/%s' % self.slug

    def __unicode__(self):
        return self.name


class Cargo(EmbeddedDocument):
    titulo = StringField()
    nombre = StringField()

    def __unicode__(self):
        return '%s: %s' % (self.titulo, self.nombre)


class Acto(Document):
    """Cada entrada de acto es un registro"""
    borme = StringField(max_length=30)
    company = StringField(max_length=200)
    id_acto = IntField()

    revocaciones = ListField(EmbeddedDocumentField(Cargo))
    reelecciones = ListField(EmbeddedDocumentField(Cargo))
    cancelaciones_oficio_nombramientos = ListField(EmbeddedDocumentField(Cargo))
    nombramientos = ListField(EmbeddedDocumentField(Cargo))

    cambio_objeto_social = StringField()
    otros_conceptos = StringField()
    fe_erratas = StringField()
    sociedad_unipersonal = StringField()
    declaracion_unipersonalidad = StringField()
    constitucion = StringField()
    suspension_pagos = StringField()
    perdida_caracter_unipersonalidad = StringField()
    datos_registrales = StringField()
    cambio_domicilio_social = StringField()
    disolucion = StringField()
    ampliacion_objeto_social = StringField()
    cierre_provisional_hoja_registral_baja_en_el_indice_entidades_juridicas = StringField()
    ceses_dimisiones = StringField()
    situacion_concursal = StringField()
    modificaciones_estatutarias = StringField()
    ampliacion_capital = StringField()
    adaptacion_ley_2_95 = StringField()
    cambio_denominacion_social = StringField()
    extincion = StringField()
    reduccion_capital = StringField()
    cambio_identidad_socio_unico = StringField()
    transformacion_sociedad = StringField()
    reapertura_hoja_registral = StringField()
    socio_unico = StringField()
    articulo_378_5_reglamento_registro_mercantil = StringField()
    fusion_absorcion = StringField()

    # Descomentar cuando haya herencias.
    #meta = {'allow_inheritance': True}

    def attributes1(self):
        d = {}
        for attr in self.__dict__['_data'].keys():
            if self.__getattribute__(attr) not in [None, '', []]:
                d[attr] = self.__getattribute__(attr)
        return d

    def attributes(self):
        l = []
        for attr in self.__dict__['_data'].keys():
            if self.__getattribute__(attr) not in [None, '', []]:
                l.append(attr)
        return l

    # Sino es imposible acceder a los valores del objeto, ya que estos contienen espacios y caracteres raros
    # FIXME: Desacoplar de borme_parser
    def __setattr__(self, name, value):
        if name not in DICT_KEYWORDS:
            super(Acto, self).__setattr__(name, value)
        else:
            if DICT_KEYWORDS[name] in ('Revocaciones', 'Reelecciones', 'Cancelaciones de oficio de nombramientos', 'Nombramientos'):
                if not isinstance(value, list):
                    raise AttributeError
                self.__setattr__(DICT_KEYWORDS[name], list(set(value)))
            else:
                self.__setattr__(DICT_KEYWORDS[name], value)

    def __unicode__(self):
        return 'Acto %d en borme %s' % (self.id_acto, self.borme)


class Config(Document):
    last_modified = DateTimeField()
