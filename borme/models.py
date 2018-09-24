# -*- coding: utf-8 -*-

from django.utils.text import slugify
from django.urls import reverse
# from django.core.exceptions import FieldError
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import SearchVectorField
from django.conf import settings

import re
from datetime import datetime

from django.db import models as m
from bormeparser.sociedad import SOCIEDADES as SOCIEDADES_DICT

SOCIEDADES = sorted(SOCIEDADES_DICT.items())
COMPANY_STATUS_CHOICES = (
    ('active', 'Activa'),
    ('suspended', 'Cierre de hoja registral'),
    ('inactive', 'Extinguida'),
    ('dissolved', 'Disuelta'),
)


class Borme(m.Model):
    """ Edicion de BORME """
    cve = m.CharField(max_length=30, primary_key=True)
    date = m.DateField(db_index=True)
    url = m.URLField(blank=True, null=True)
    from_reg = m.IntegerField()
    until_reg = m.IntegerField()
    province = m.CharField(max_length=100)
    section = m.CharField(max_length=20)
    # pages = IntegerField()
    anuncios = JSONField(default=list)

    @property
    def total_anuncios(self):
        return len(self.anuncios)

    def get_absolute_url(self):
        return reverse('borme-borme', args=[str(self.cve)])

    def __str__(self):
        return self.cve


class Person(m.Model):
    """ Persona """
    name = m.CharField(max_length=200, db_index=True)
    slug = m.SlugField(max_length=200, primary_key=True)
    in_companies = JSONField(default=list)
    in_bormes = JSONField(default=list)

    date_updated = m.DateField(db_index=True)
    cargos_actuales = JSONField(default=list)
    cargos_historial = JSONField(default=list)

    document = SearchVectorField(null=True, db_index=True)

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
        Todos los cargos vigentes que ocupe en la sociedad extinguida pasan a
        estar en la lista de cargos cesados.
        company: str
        date: str iso format
        """
        for cargo in self.cargos_actuales:
            if cargo['name'] == company:
                self.cargos_actuales.remove(cargo)
                cargo['date_to'] = date
                self.cargos_historial.append(cargo)

    def get_cargos_actuales(self, offset=0, limit=settings.CARGOS_LIMIT):
        """ Devuelve el listado de cargos actuales de una sociedad y si hace
        falta mostrar más (paginación)

        :rtype: (list, bool)
        """
        cargos = self.cargos_actuales.copy()
        cargos = [dict(item, **{'type': 'company'}) for item in cargos]
        cargos = sorted(cargos, key=lambda k: k['date_from'])

        if limit == 0:
            limit = len(cargos)
        show_more = offset+limit < len(cargos)

        return cargos[offset:offset+limit], show_more

    def get_cargos_historial(self, offset=0, limit=settings.CARGOS_LIMIT):
        """ Devuelve el listado de cargos pasados de una sociedad y si hace
        falta mostrar más (paginación)

        :rtype: (list, bool)
        """
        cargos = self.cargos_historial.copy()
        cargos = [dict(item, **{'type': 'company'}) for item in cargos]
        cargos = sorted(cargos, key=lambda k: k['date_to'])

        if limit == 0:
            limit = len(cargos)
        show_more = offset+limit < len(cargos)

        return cargos[offset:offset+limit], show_more

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


class Company(m.Model):
    """ Sociedad """
    name = m.CharField(max_length=260, db_index=True)
    nif = m.CharField(max_length=10, blank=True, null=True)
    capital = m.IntegerField(blank=True, null=True)
    inicio_actividad = m.DateField(blank=True, null=True)
    domicilio = m.CharField(max_length=260, blank=True, null=True)
    objeto = m.CharField(max_length=1000, blank=True, null=True)
    slug = m.SlugField(max_length=260, primary_key=True)
    date_creation = m.DateField(blank=True, null=True)
    date_extinction = m.DateField(blank=True, null=True)
    date_dissolution = m.DateField(blank=True, null=True)
    type = m.CharField(max_length=50, choices=SOCIEDADES)
    auditors = JSONField(default=list)
    liquidators = JSONField(default=list)
    reason_dissolution = m.CharField(max_length=50, blank=True, null=True)
    status = m.CharField(max_length=50, choices=COMPANY_STATUS_CHOICES,
                         default='active')

    date_updated = m.DateField(db_index=True)
    in_bormes = JSONField(default=list)
    anuncios = JSONField(default=list)

    cargos_actuales_p = JSONField(default=list)
    cargos_actuales_c = JSONField(default=list)
    cargos_historial_p = JSONField(default=list)
    cargos_historial_c = JSONField(default=list)

    document = SearchVectorField(null=True, db_index=True)

    def add_auditor(self, auditor_name, type_, date):
        auditor = {'name': auditor_name, 'type': type_, 'date_from': date}
        self.auditors = [auditor] + self.auditors

    def last_auditor(self):
        if self.auditors:
            return self.auditors[0]
        return False

    def add_liquidator(self, liquid_name, type_, date):
        liquidator = {'name': liquid_name, 'type': type_, 'date_from': date}
        self.liquidators = [liquidator] + self.liquidators

    def add_in_bormes(self, borme):
        if borme not in self.in_bormes:
            self.in_bormes.append(borme)

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def total_anuncios(self):
        return len(self.anuncios)

    @property
    def total_bormes(self):
        return len(self.in_bormes)

    @property
    def fullname(self):
        return "{} {}".format(self.name.title(), self.type)

    def get_cargos_actuales(self, offset=0, limit=settings.CARGOS_LIMIT):
        cargos_p = self.cargos_actuales_p.copy()
        cargos_c = self.cargos_actuales_c.copy()
        cargos_p = [dict(item, **{'type': 'person'}) for item in cargos_p]
        cargos_c = [dict(item, **{'type': 'company'}) for item in cargos_c]
        cargos = sorted(cargos_p + cargos_c, key=lambda k: k['date_from'])

        if limit == 0:
            limit = len(cargos)
        show_more = offset+limit < len(cargos)

        return cargos[offset:offset+limit], show_more

    def get_cargos_historial(self, offset=0, limit=settings.CARGOS_LIMIT):
        cargos_p = self.cargos_historial_p.copy()
        cargos_c = self.cargos_historial_c.copy()
        cargos_p = [dict(item, **{'type': 'person'}) for item in cargos_p]
        cargos_c = [dict(item, **{'type': 'company'}) for item in cargos_c]
        cargos = sorted(cargos_p + cargos_c, key=lambda k: k['date_to'])

        if limit == 0:
            limit = len(cargos)
        show_more = offset+limit < len(cargos)

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
        # TODO:
        # Cambiar SOCIEDAD LIMITADA por SL,
        # SOCIEDAD ANONIMA por SA, COOP, SCL...
        # if self.name.endswith('SOCIEDAD LIMITADA'): ...

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
        """ Se llama a este método cuando una sociedad se extingue.
        Todos los cargos vigentes que ocupe en la sociedad extinguida pasan a
        estar en la lista de cargos cesados.
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


class Anuncio(m.Model):
    id_anuncio = m.IntegerField()
    year = m.IntegerField()
    borme = m.ForeignKey('Borme', on_delete=m.PROTECT)
    company = m.ForeignKey('Company', on_delete=m.PROTECT)
    datos_registrales = m.CharField(max_length=70)
    actos = JSONField(default=list)

    class Meta:
        unique_together = ('id_anuncio', 'year')
        index_together = ['id_anuncio', 'year']

    @property
    def total_actos(self):
        return len(self.actos)

    @property
    def date(self):
        regexp = r'\(\s*\d{1,2}\.\d{2}\.\d{2}\)\.'
        fecha = re.findall(regexp, self.datos_registrales)[0]
        return datetime.strptime(fecha, '(%d.%m.%y).').date()

    def get_absolute_url(self):
        year = str(self.year)
        anuncio_id = str(self.id_anuncio)
        return reverse('borme-anuncio', args=[year, anuncio_id])

    def __str__(self):
        return '%d - %d (%d actos)' % (
                    self.id_anuncio, self.year, len(self.actos))


class Config(m.Model):
    last_modified = m.DateTimeField()
    version = m.CharField(max_length=50)


class BormeLog(m.Model):
    borme = m.OneToOneField('Borme', primary_key=True, on_delete=m.PROTECT)
    date_created = m.DateTimeField(auto_now_add=True)
    date_updated = m.DateTimeField(auto_now=True)
    date_parsed = m.DateTimeField(blank=True, null=True)
    parsed = m.BooleanField(default=False)
    errors = m.IntegerField(default=0)
    path = m.CharField(max_length=200)

    def __str__(self):
        return 'Log(%s): %d errors' % (self.borme.cve, self.errors)


def anuncio_get_or_create(anuncio, year, borme):
    """Devuelve una instancia de Anuncio.

    :rtype: (borme.models.Anuncio, bool anuncio created)
    """

    try:
        nuevo_anuncio = Anuncio.objects.get(id_anuncio=anuncio.id, year=year)
        created = False
    except Anuncio.DoesNotExist:
        nuevo_anuncio = Anuncio(
                        id_anuncio=anuncio.id,
                        year=year,
                        borme=borme,
                        datos_registrales=anuncio.datos_registrales)
        created = True

    return nuevo_anuncio, created


def company_get_or_create(empresa, tipo, slug_c):
    """Devuelve una instancia de Company.

    :rtype: (borme.models.Company, bool company created)
    """

    try:
        company = Company.objects.get(slug=slug_c)
        created = False
    except Company.DoesNotExist:
        company = Company(name=empresa, type=tipo)
        created = True

    return company, created


def person_get_or_create(nombre):
    """Devuelve una instancia de Person.

    :rtype: (borme.models.Person, bool person created)
    """

    try:
        slug_p = slugify(nombre)
        person = Person.objects.get(slug=slug_p)
        created = False
    except Person.DoesNotExist:
        person = Person(name=nombre)
        created = True

    return person, created


def borme_get_or_create(_borme):
    """Devuelve una instancia de Borme.

    :param _borme: Instancia BORME
    :param filename: Nombre del archivo BORME-PDF
    :type borme: bormeparser.parser.backend.BormeBase
    :type filename: str
    :rtype: (borme.models.BormeLog, bool bormelog created)
    """

    try:
        borme = Borme.objects.get(cve=_borme.cve)
        created = False
    except Borme.DoesNotExist:
        borme = Borme(cve=_borme.cve, date=_borme.date, url=_borme.url,
                      from_reg=_borme.anuncios_rango[0],
                      until_reg=_borme.anuncios_rango[1],
                      province=_borme.provincia,
                      section=_borme.seccion)
        borme.save()
        # type, num?, filename?
        created = True

    return borme, created


def bormelog_get_or_create(_borme):
    """Devuelve una instancia de BormeLog.

    :param _borme: Instancia BORME
    :param filename: Nombre del archivo BORME-PDF
    :type _borme: borme.models.Borme
    :type filename: str
    :rtype: (borme.models.BormeLog, bool bormelog created)
    """

    try:
        borme_log = BormeLog.objects.get(borme=_borme)
        created = False
    except BormeLog.DoesNotExist:
        borme_log = BormeLog(borme=_borme, path='TODO_REMOVE')
        created = True

    return borme_log, created


def get_borme_urls_from_slug(slug):
    try:
        entity = Person.objects.get(slug=slug)
    except Person.DoesNotExist:
        try:
            entity = Company.objects.get(slug=slug)
        except Company.DoesNotExist:
            return []

    return [b["url"] for b in entity.in_bormes]
