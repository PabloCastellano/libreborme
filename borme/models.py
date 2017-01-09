# -*- coding: utf-8 -*-

from django.utils.text import slugify
from django.core.urlresolvers import reverse
# from django.core.exceptions import FieldError
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

from django.db.models import *
from bormeparser.regex import SOCIEDADES as SOCIEDADES_DICT
from django_hstore import hstore

SOCIEDADES = sorted(SOCIEDADES_DICT.items())

"""
# TODO: i18n 2o valor
PROVINCES = (
    ('Malaga', 'Málaga'),
    ('Sevilla', 'Sevilla'),
    ('Granada', 'Granada'),
)
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
    anuncios = ArrayField(IntegerField(), default=list)  # FIXME: {year, id}

    @property
    def total_anuncios(self):
        return len(self.anuncios)

    def get_absolute_url(self):
        return reverse('borme-borme', args=[str(self.cve)])

    def __str__(self):
        return self.cve


class Person(Model):
    """ Persona """
    name = CharField(max_length=200, db_index=True)
    slug = CharField(max_length=200, primary_key=True)
    in_companies = ArrayField(CharField(max_length=260), default=list)
    in_bormes = ArrayField(hstore.DictionaryField(), default=list)

    date_updated = DateField(db_index=True)
    cargos_actuales = ArrayField(hstore.DictionaryField(), default=list)
    cargos_historial = ArrayField(hstore.DictionaryField(), default=list)

    # last access
    # number of visits

    def add_in_companies(self, company):
        if company not in self.in_companies:
            self.in_companies.append(company)

    def add_in_bormes(self, borme):
        if borme not in self.in_bormes:
            self.in_bormes.append(borme)

    def update_cargos_entrantes(self, cargos):
        """ cargos = [dict] """
        self.cargos_actuales.extend(cargos)

    def update_cargos_salientes(self, cargos):
        """ cargos = [dict] """

        for cargo in cargos:
            for cargo_a in self.cargos_actuales:
                if all(cargo[k] == cargo_a[k] for k in ('name', 'title')):
                    self.cargos_actuales.remove(cargo_a)
                    cargo['date_from'] = cargo_a['date_from']
                    break
            self.cargos_historial.append(cargo)

    def _cesar_cargo(self, company, date):
        """ Se llama a este método cuando una sociedad se extingue.
            Todos los cargos vigentes que ocupe en la sociedad extinguida pasan a estar en la lista de cargos cesados.
            company: str
            date: str iso format
        """
        for cargo in self.cargos_actuales:
            if cargo['name'] == company:
                self.cargos_actuales.remove(cargo)
                cargo['date_to'] = date
                self.cargos_historial.append(cargo)

    @property
    def total_companies(self):
        return len(self.in_companies)

    @property
    def total_bormes(self):
        return len(self.in_bormes)

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
    name = CharField(max_length=260, db_index=True)
    nif = CharField(max_length=10)
    slug = CharField(max_length=260, primary_key=True)
    date_creation = DateField(blank=True, null=True)
    date_extinction = DateField(blank=True, null=True)
    is_active = BooleanField(default=True)
    type = CharField(max_length=50, choices=SOCIEDADES)

    date_updated = DateField(db_index=True)
    in_bormes = ArrayField(hstore.DictionaryField(), default=list)
    anuncios = ArrayField(IntegerField(), default=list)  # FIXME: {year, id}

    cargos_actuales_p = ArrayField(hstore.DictionaryField(), default=list)
    cargos_actuales_c = ArrayField(hstore.DictionaryField(), default=list)
    cargos_historial_p = ArrayField(hstore.DictionaryField(), default=list)
    cargos_historial_c = ArrayField(hstore.DictionaryField(), default=list)

    def add_in_bormes(self, borme):
        if borme not in self.in_bormes:
            self.in_bormes.append(borme)

    @property
    def total_anuncios(self):
        return len(self.anuncios)

    @property
    def total_bormes(self):
        return len(self.in_bormes)

    @property
    def fullname(self):
        return '%s %s' % (self.name.title(), self.type)

    def get_cargos_actuales(self, offset=0, limit=settings.CARGOS_LIMIT):
        cargos_p = self.cargos_actuales_p.copy()
        cargos_c = self.cargos_actuales_c.copy()
        cargos_p = [dict(item, **{'type': 'person'}) for item in cargos_p]
        cargos_c = [dict(item, **{'type': 'company'}) for item in cargos_c]
        cargos = sorted(cargos_p + cargos_c, key=lambda k: k['date_from'])

        show_more = offset+limit < len(cargos)
        if limit == 0: limit = len(cargos)

        return cargos[offset:offset+limit], show_more

    def get_cargos_historial(self, offset=0, limit=settings.CARGOS_LIMIT):
        cargos_p = self.cargos_historial_p.copy()
        cargos_c = self.cargos_historial_c.copy()
        cargos_p = [dict(item, **{'type': 'person'}) for item in cargos_p]
        cargos_c = [dict(item, **{'type': 'company'}) for item in cargos_c]
        cargos = sorted(cargos_p + cargos_c, key=lambda k: k['date_to'])

        show_more = offset+limit < len(cargos)
        if limit == 0: limit = len(cargos)

        return cargos[offset:offset+limit], show_more

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
        """ cargos = [dict] """

        for cargo in cargos:
            cargo_embed = cargo.copy()
            if cargo_embed['type'] == 'company':
                del cargo_embed['type']
                self.cargos_actuales_c.append(cargo_embed)
            elif cargo_embed['type'] == 'person':
                del cargo_embed['type']
                self.cargos_actuales_p.append(cargo_embed)

    def update_cargos_salientes(self, cargos):
        """ cargos = [dict] """

        for cargo in cargos:
            cargo_embed = cargo.copy()
            if cargo_embed['type'] == 'company':
                del cargo_embed['type']
                for cargo_a in self.cargos_actuales_c:
                    if all(cargo[k] == cargo_a[k] for k in ('name', 'title')):
                        self.cargos_actuales_c.remove(cargo_a)
                        cargo_embed['date_from'] = cargo_a['date_from']
                        break
                self.cargos_historial_c.append(cargo_embed)
            elif cargo_embed['type'] == 'person':
                del cargo_embed['type']
                for cargo_a in self.cargos_actuales_p:
                    if all(cargo[k] == cargo_a[k] for k in ('name', 'title')):
                        self.cargos_actuales_p.remove(cargo_a)
                        cargo_embed['date_from'] = cargo_a['date_from']
                        break
                self.cargos_historial_p.append(cargo_embed)
            else:
                raise ValueError('type: invalid value')
            
    def _cesar_cargo(self, company, date):
        """
            company: str
            date: str iso format
        """
        for cargo in self.cargos_actuales_c:
            if cargo['name'] == company:
                self.cargos_actuales_c.remove(cargo)
                cargo['date_to'] = date
                self.cargos_historial_c.append(cargo)
        
    def get_absolute_url(self):
        return reverse('borme-empresa', args=[str(self.slug)])

    def __str__(self):
        return self.fullname


class Anuncio(Model):
    id_anuncio = IntegerField()
    year = IntegerField()
    borme = ForeignKey('Borme')
    company = ForeignKey('Company')
    datos_registrales = CharField(max_length=70)
    actos = hstore.SerializedDictionaryField()  # TODO: schema={...}  # TODO: Actos repetidos

    class Meta:
        index_together = ['id_anuncio', 'year']

    #objects = hstore.HStoreManager()

    @property
    def total_actos(self):
        return len(self.actos)

    def get_absolute_url(self):
        return reverse('borme-anuncio', args=[str(self.year), str(self.id_anuncio)])

    def __str__(self):
        return '%d - %d (%d actos)' % (self.id_anuncio, self.year, len(self.actos.keys()))


class Config(Model):
    last_modified = DateTimeField()
    version = CharField(max_length=50)


class BormeLog(Model):
    borme = OneToOneField('Borme', primary_key=True)
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)
    date_parsed = DateTimeField(blank=True, null=True)
    parsed = BooleanField(default=False)
    errors = IntegerField(default=0)
    path = CharField(max_length=200)

    def __str__(self):
        return 'Log(%s): %d errors' % (self.borme.cve, self.errors)
