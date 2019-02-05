"""
The Follower table stores subscriptions to companies and people.
The AlertActo table stored subscriptions to events.
"""
from django.db import models as m
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    ('daily', 'Diaria')
)
PERIODICIDAD_DICT = dict(PERIODICIDAD_CHOICES)

PAYMENT_CHOICES = (
    ('stripe', "Stripe"),
    ('bank', "Transferencia bancaria"),
    # ('bitcoin', "Bitcoin")
)

EVENTOS_CHOICES = (
    # ('con', 'Concursos de acreedores'),
    ('liq', 'Liquidación de empresas'),
    ('new', 'Empresas de nueva creación'),
    ('adm', 'Cambios de administrador'),
)
EVENTOS_DICT = dict(EVENTOS_CHOICES)


ALERTAS_CHOICES = EVENTOS_CHOICES
ALERTAS_CHOICES += (
    ('company', "Empresa"),
    ('person', "Persona"),
)

FOLLOW_CHOICES = (
    ('company', "Empresa"),
    ('person', "Persona"),
)


# Reference:
# https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = m.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class AlertaActo(m.Model):
    """ This table stores event subscriptions by users
    """
    user = m.ForeignKey(get_user_model(), on_delete=m.PROTECT)
    evento = m.CharField(max_length=3, choices=EVENTOS_CHOICES)
    provincia = m.CharField(max_length=100, choices=PROVINCIAS_CHOICES)
    is_enabled = m.BooleanField(default=True)
    periodicidad = m.CharField(max_length=10, choices=PERIODICIDAD_CHOICES)

    def __str__(self):
        enabled = "activada" if self.is_enabled else "desactivada"
        return "Alerta {} para evento {}".format(enabled, EVENTOS_DICT[self.evento])


# UNUSED: should be removed at some time if proven useless
class LBInvoice(m.Model):
    """ This table stores event subscriptions by users
    """
    user = m.ForeignKey(get_user_model(), on_delete=m.PROTECT)
    start_date = m.DateTimeField()
    end_date = m.DateTimeField()
    amount = m.FloatField()
    payment_type = m.CharField(max_length=10, choices=PAYMENT_CHOICES)
    name = m.CharField(max_length=100)
    email = m.EmailField(max_length=100)
    address = m.CharField(max_length=200)
    nif = m.CharField(max_length=20, blank=True)
    ip = m.GenericIPAddressField(unpack_ipv4=True)
    description = m.CharField(max_length=2000, blank=True)
    subscription_id = m.CharField(max_length=200)

    # TODO: unused, remove
    @property
    def is_paid(self):
        return True

    def get_absolute_url(self):
        return reverse('alertas-invoice-view', args=[str(self.id)])

    def __str__(self):
        return "LBInvoice ({}): {}".format(self.user, self.amount)


class AlertasConfig(m.Model):
    """ This table stores the configuration of this Django app
    """
    key = m.CharField(max_length=30, primary_key=True)
    value = m.CharField(max_length=100)

    def __str__(self):
        return "{}: {}".format(self.key, self.value)


class AlertaHistory(m.Model):
    """ This table stores the history of alerts sent to users
    """
    user = m.ForeignKey(get_user_model(), on_delete=m.PROTECT)
    type = m.CharField(max_length=10, choices=ALERTAS_CHOICES)
    date = m.DateField()
    provincia = m.CharField(max_length=100, choices=PROVINCIAS_CHOICES, blank=True, null=True)
    entidad = m.CharField(max_length=260, blank=True, null=True)
    periodicidad = m.CharField(max_length=10, choices=PERIODICIDAD_CHOICES, blank=True, null=True)

    def get_csv_path(self):
        # TODO: provincia and periodicidad can be blank
        year = str(self.date.year)
        month = "{:02d}".format(self.date.month)
        day = "{:02d}".format(self.date.day)
        provincia = PROVINCIAS_DICT[self.provincia].replace(" ", "_")
        path = os.path.join(settings.BORME_ROOT, "csv_alertas", provincia)
        path = os.path.join(path, self.periodicidad, year, month, day + "_" + self.type + ".csv")
        return path

    def __str__(self):
        return "{0}, {1}, {2}".format(self.type, self.date, self.user.username)


class LibrebormeLogs(m.Model):
    """ This table stores the history of events in Libreborme
    """
    date = m.DateField(auto_now_add=True)
    component = m.CharField(max_length=100)
    log = m.CharField(max_length=1000)
    user = m.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "{0} ({1}): {2}".format(self.component, self.date, self.log)


class Follower(m.Model):
    """ This table stores the Followers

    Users follow companies and people to receive alerts when they are updated
    """
    user = m.ForeignKey(get_user_model(), on_delete=m.PROTECT)
    slug = m.SlugField(max_length=200)
    type = m.CharField(max_length=10, choices=FOLLOW_CHOICES)
    date_created = m.DateField(auto_now_add=True)
    is_enabled = m.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'slug', 'type']

    # FIXME: Now the slug existence is checked in the ajax call in the view
    """
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Follower, self).save(*args, **kwargs)
    """

    @classmethod
    def toggle_follow(cls, user, slug, type_):
        instance = cls.objects.filter(user=user, slug=slug, type=type_)
        if instance.exists():
            instance.delete()
            return False
        else:
            cls.objects.create(user=user, slug=slug, type=type_)
            return True

    @property
    def name(self):
        if self.type == "person":
            cls = Person
        elif self.type == "company":
            cls = Company
        return cls.objects.get(slug=self.slug).name

    @property
    def last_update(self):
        if not hasattr(self, '_last_update'):
            if self.type == 'person':
                obj = Person.objects.get(slug=self.slug)
            elif self.type == 'company':
                obj = Company.objects.get(slug=self.slug)
            self._last_update = obj.date_updated
        return self._last_update

    def get_absolute_url(self):
        if self.type == "person":
            return reverse('borme-persona', args=[str(self.slug)])
        elif self.type == "company":
            return reverse('borme-empresa', args=[str(self.slug)])

    def __str__(self):
        return "{0} is following {1}".format(self.user, self.slug)
