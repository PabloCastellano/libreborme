# -*- coding: utf-8 -*-

from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError
from django.contrib.postgres.fields import ArrayField

from django.db.models import *
from bormeparser.regex import SOCIEDADES as SOCIEDADES_DICT
from django_hstore import hstore

#from borme_parser import DICT_KEYWORDS
DICT_KEYWORDS = {}  # FIXME
SOCIEDADES = sorted(SOCIEDADES_DICT.items())

# TODO: i18n 2o valor
PROVINCES = (
    ('Malaga', 'Málaga'),
    ('Sevilla', 'Sevilla'),
    ('Granada', 'Granada'),
)


"""
class CargoCompany(Model):
    title = CharField(max_length=50)
    name = ForeignKey('Company')
    date_from = DateTimeField()
    date_to = DateField()

    def get_absolute_url(self):
        slug = slugify(self.name)
        return reverse('borme-empresa', args=[slug])

    def __str__(self):
        d_from = ''
        d_to = ''
        if self.date_from:
            d_from = 'From: %s' % self.date_from.strftime('%x')
        if self.date_to:
            d_to = 'To: %s' % self.date_to.strftime('%x')
        return '%s: %s (%s %s)' % (self.title, self.name, d_from, d_to)


# TODO: subclass CargoCompany
class CargoPerson(Model):
    title = CharField(max_length=50)
    name = ForeignKey('Person')
    date_from = DateTimeField()
    date_to = DateField()

    def get_absolute_url(self):
        slug = slugify(self.name)
        return reverse('borme-persona', args=[slug])

    def __str__(self):
        d_from = ''
        d_to = ''
        if self.date_from:
            d_from = 'From: %s' % self.date_from.strftime('%x')
        if self.date_to:
            d_to = 'To: %s' % self.date_to.strftime('%x')
        return '%s: %s (%s %s)' % (self.title, self.name, d_from, d_to)
"""


class Borme(Model):
    """ Edicion de BORME """
    cve = CharField(max_length=30, primary_key=True)
    date = DateField()
    url = URLField()
    from_reg = IntegerField()
    until_reg = IntegerField()
    #province = CharField(max_length=100, choices=PROVINCES)
    province = CharField(max_length=100)
    section = CharField(max_length=20)
    #pages = IntegerField()
    anuncios = ArrayField(IntegerField(), default=list)

    def get_absolute_url(self):
        return reverse('borme-borme', args=[str(self.cve)])

    def __str__(self):
        return self.cve


class Person(Model):
    """ Persona """
    name = CharField(max_length=200, db_index=True)
    slug = CharField(max_length=200, primary_key=True)
    in_companies = ArrayField(CharField(max_length=250), default=list)
    in_bormes = ArrayField(hstore.DictionaryField(), default=list)

    date_updated = DateField()
    cargos_actuales = ArrayField(hstore.DictionaryField(), default=list)
    cargos_historial = ArrayField(hstore.DictionaryField(), default=list)

    # last access
    # number of visits

    def add_in_companies(self, company):
        if not company in self.in_companies:
            self.in_companies.append(company)

    def add_in_bormes(self, borme):
        if not borme in self.in_bormes:
            self.in_bormes.append(borme)

    def update_cargos_entrantes(self, cargos):
        """ cargos = [CargoCompany] """
        self.cargos_actuales.extend(cargos)

    def update_cargos_salientes(self, cargos):
        """ cargos = [CargoCompany] """

        for cargo in cargos:
            if cargo in self.cargos_actuales:
                self.cargos_actuales.remove(cargo)
            self.cargos_historial.append(cargo)

    @property
    def todos_cargos(self):
        return self.cargos_actuales + self.cargos_historial

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Person, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('borme-persona', args=[str(self.slug)])

    def __str__(self):
        return self.name


class Company(Model):
    """ Sociedad """
    name = CharField(max_length=250, db_index=True)
    nif = CharField(max_length=10)
    slug = CharField(max_length=250, primary_key=True)
    date_creation = DateField(blank=True, null=True)
    is_active = BooleanField(default=False)
    type = CharField(max_length=50, choices=SOCIEDADES)

    date_updated = DateField()
    in_bormes = ArrayField(hstore.DictionaryField(), default=list)
    anuncios = ArrayField(IntegerField(), default=list)

    cargos_actuales_p = ArrayField(hstore.DictionaryField(), default=list)
    cargos_actuales_c = ArrayField(hstore.DictionaryField(), default=list)
    cargos_historial_p = ArrayField(hstore.DictionaryField(), default=list)
    cargos_historial_c = ArrayField(hstore.DictionaryField(), default=list)

    def add_in_bormes(self, borme):
        if not borme in self.in_bormes:
            self.in_bormes.append(borme)

    @property
    def cargos_actuales(self):
        return self.cargos_actuales_p + self.cargos_actuales_c

    @property
    def cargos_historial(self):
        return self.cargos_historial_p + self.cargos_historial_c

    @property
    def todos_cargos_c(self):
        return self.cargos_actuales_c + self.cargos_historial_c

    @property
    def todos_cargos_p(self):
        return self.cargos_actuales_p + self.cargos_historial_p

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
            if cargo['type'] == 'company':
                del cargo['type']
                self.cargos_actuales_c.append(cargo)
            elif cargo['type'] == 'person':
                del cargo['type']
                self.cargos_actuales_p.append(cargo)

    def update_cargos_salientes(self, cargos):
        """ cargos = [CargoCompany/CargoPerson] """

        for cargo in cargos:
            if cargo['type'] == 'company':
                del cargo['type']
                if cargo in self.cargos_actuales_c:
                    self.cargos_actuales_c.remove(cargo)
                self.cargos_historial_c.append(cargo)
            elif cargo['type'] == 'person':
                del cargo['type']
                if cargo in self.cargos_actuales_p:
                    self.cargos_actuales_p.remove(cargo)
                self.cargos_historial_p.append(cargo)

    def get_absolute_url(self):
        return reverse('borme-empresa', args=[str(self.slug)])

    def __str__(self):
        return self.name


class Anuncio(Model):
    id_anuncio = IntegerField(primary_key=True)
    borme = ForeignKey('Borme')
    company = ForeignKey('Company')
    year = IntegerField()
    datos_registrales = CharField(max_length=70)
    actos = hstore.SerializedDictionaryField()  # TODO: schema={...}  # TODO: Actos repetidos

    class Meta:
        index_together = ['id_anuncio', 'year']

    #objects = hstore.HStoreManager()

    def get_absolute_url(self):
        return reverse('borme-anuncio', args=[str(self.year), str(self.id_anuncio)])

    def __str__(self):
        return '%d - %d (%d actos)' % (self.id_anuncio, self.year, len(self.actos.keys()))


class Config(Model):
    last_modified = DateTimeField()
    version = CharField(max_length=50)


class BormeLog(Model):
    borme = ForeignKey('Borme')
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)
    date_parsed = DateTimeField(blank=True, null=True)
    parsed = BooleanField(default=False)
    errors = IntegerField(default=0)
    path = CharField(max_length=200)

    def __str__(self):
        return 'Log(%s): %d errors' % (self.borme.cve, self.errors)
