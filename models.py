from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from borme.models import Company, Person

import os.path


PROVINCIAS_CHOICES = (
    ('1', 'Álava'),
    ('2', 'Albacete'),
    ('3', 'Alicante'),
    ('4', 'Almería'),
    ('5', 'Ávila'),
    ('6', 'Badajoz'),
    ('7', 'Islas Baleares'),
    ('8', 'Barcelona'),
    ('9', 'Burgos'),
    ('10', 'Cáceres'),
    ('11', 'Cádiz'),
    ('12', 'Castellón'),
    ('13', 'Ciudad Real'),
    ('14', 'Córdoba'),
    ('15', 'La Coruña'),
    ('16', 'Cuenca'),
    ('17', 'Gerona'),
    ('18', 'Granada'),
    ('19', 'Guadalajara'),
    ('20', 'Guipúzcoa'),
    ('21', 'Huelva'),
    ('22', 'Huesca'),
    ('23', 'Jaén'),
    ('24', 'León'),
    ('25', 'Lérida'),
    ('26', 'La Rioja'),
    ('27', 'Lugo'),
    ('28', 'Madrid'),
    ('29', 'Málaga'),
    ('30', 'Murcia'),
    ('31', 'Navarra'),
    ('32', 'Orense'),
    ('33', 'Asturias'),
    ('34', 'Palencia'),
    ('35', 'Las Palmas'),
    ('36', 'Pontevedra'),
    ('37', 'Salamanca'),
    ('38', 'Santa Cruz de Tenerife'),
    ('39', 'Cantabria'),
    ('40', 'Segovia'),
    ('41', 'Sevilla'),
    ('42', 'Soria'),
    ('43', 'Tarragona'),
    ('44', 'Teruel'),
    ('45', 'Toledo'),
    ('46', 'Valencia'),
    ('47', 'Valladolid'),
    ('48', 'Vizcaya'),
    ('49', 'Zamora'),
    ('50', 'Zaragoza'),
    ('51', 'Ceuta'),
    ('52', 'Melilla')
)
PROVINCIAS_DICT = dict(PROVINCIAS_CHOICES)

PERIODICIDAD_CHOICES = (
    ('weekly', 'Semanal'),
    ('monthly', 'Mensual'),
    ('daily', 'Diario')
)
PERIODICIDAD_DICT = dict(PERIODICIDAD_CHOICES)

ACCOUNT_CHOICES = (
    ('free', "Gratuita"),
    ('paid', "Premium"),
    ('test', "Período de prueba"),
)

PAYMENT_CHOICES = (
    ('paypal', "Paypal"),
    ('bank', "Transferencia bancaria"),
    #('bitcoin', "Bitcoin")
)

NOTIFICATION_CHOICES = (
    ('email', "E-mail"),
    ('url', "URL"),
    #('telegram', "Telegram"),
)

EVENTOS_CHOICES = (
    ('con', 'Concursos de acreedores'),
    ('liq', 'Liquidación de empresas'),
    ('new', 'Empresas de nueva creación'),
)
EVENTOS_DICT = dict(EVENTOS_CHOICES)


ALERTAS_CHOICES = EVENTOS_CHOICES
ALERTAS_CHOICES += (
    ('company', "Empresa"),
    ('person', "Persona"),
)

LANGUAGE_CHOICES = (
    ('es', 'Español'),
)

User._meta.get_field('email').blank = False


# TODO: agrupar todas las alertas en una misma tabla?

class AlertaCompany(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    is_enabled = models.BooleanField(default=True)
    send_html = models.BooleanField(default=True)

    def __str__(self):
        enabled = "activada" if self.is_enabled else "desactivada"
        return "Alerta {} para la empresa {}".format(enabled, self.company)


class AlertaPerson(models.Model):
    user = models.ForeignKey(User)
    person = models.ForeignKey(Person)
    is_enabled = models.BooleanField(default=True)
    send_html = models.BooleanField(default=True)

    def __str__(self):
        enabled = "activada" if self.is_enabled else "desactivada"
        return "Alerta {} para la persona {}".format(enabled, self.person)


class AlertaActo(models.Model):
    user = models.ForeignKey(User)
    evento = models.CharField(max_length=3, choices=EVENTOS_CHOICES)
    provincia = models.CharField(max_length=100, choices=PROVINCIAS_CHOICES)
    is_enabled = models.BooleanField(default=True)
    send_html = models.BooleanField(default=True)
    periodicidad = models.CharField(max_length=10, choices=PERIODICIDAD_CHOICES)

    def __str__(self):
        enabled = "activada" if self.is_enabled else "desactivada"
        return "Alerta {} para evento {}".format(enabled, EVENTOS_DICT[self.evento])


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=4, choices=ACCOUNT_CHOICES)
    notification_method = models.CharField(max_length=10, choices=NOTIFICATION_CHOICES, default='email')
    notification_email = models.EmailField(blank=True)
    notification_url = models.URLField(blank=True)
    language = models.CharField(max_length=3, choices=LANGUAGE_CHOICES, default='es')

    def save(self, force_insert=False, force_update=False):
        if not self.notification_email:
            self.notification_email = self.user.email
        super(Profile, self).save(force_insert, force_update)

    def is_premium(self):
        pass
        #return all(for invoice in self.invoices:
        #    invoice

    def __str__(self):
        return "Profile {} ({})".format(self.user, self.account_type)


class LBInvoice(models.Model):
    user = models.ForeignKey(User)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount = models.FloatField()
    type = models.CharField(max_length=10, blank=True)  # reservado
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    is_paid = models.BooleanField()
    description = models.CharField(max_length=2000, blank=True)
    nif = models.CharField(max_length=20)

    def get_absolute_url(self):
        return reverse('alertas-invoice-view', args=[str(self.id)])

    def __str__(self):
        return "LBInvoice ({}): {}. Pagada: {}".format(self.user, self.amount, self.is_paid)


class AlertasConfig(models.Model):
    key = models.CharField(max_length=30, primary_key=True)
    value = models.CharField(max_length=100)

    def __str__(self):
        return "{}: {}".format(self.key, self.value)


class AlertaHistory(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(max_length=10, choices=ALERTAS_CHOICES)
    date = models.DateField()
    provincia = models.CharField(max_length=3, choices=PROVINCIAS_CHOICES, blank=True, null=True)
    entidad = models.CharField(max_length=260, blank=True, null=True)
    periodicidad = models.CharField(max_length=10, choices=PERIODICIDAD_CHOICES, blank=True, null=True)

    def get_csv_path(self):
        # TODO: provicnia and periodicidad can be blank
        year = str(self.date.year)
        month = "{:02d}".format(self.date.month)
        day = "{:02d}".format(self.date.day)
        provincia = PROVINCIAS_DICT[self.provincia].replace(" ", "_")
        path = os.path.join(settings.BORME_ROOT, "csv_alertas", provincia)
        path = os.path.join(path, self.periodicidad, year, month, day + "_" + self.type + ".csv")
        return path

    def __str__(self):
        return "{0}, {1}, {2}".format(self.type, self.date, self.user.username)


# max_alertas_free_company

# Tipos de alerta:
#    - Sale una empresa a la que está suscrita (suscripción por empresa)
#    - Sale una persona a la que está suscrito (suscripción por persona)
#    - Sale algún acto mercantil al que se está suscrito (suscripción por acto)
#        - En liquidación
#        - Concurso de acreedores
