from django.db import models

from django.contrib.auth.models import User

from borme.models import Company, Person

# User = get_model_user...

PERIODICIDAD_CHOICES = (
    ('W', 'Weekly'),
    ('M', 'Monthly'),
    ('D', 'Daily')
)


EVENTOS_CHOICES = (
    ('CON', 'Concurso de acreedores'),
    ('LIQ', 'Liquidación'),
)
EVENTOS_DICT = dict(EVENTOS_CHOICES)


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
    provincia = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True)
    send_html = models.BooleanField(default=True)
    periodicidad = models.CharField(max_length=1, choices=PERIODICIDAD_CHOICES)

    def __str__(self):
        enabled = "activada" if self.is_enabled else "desactivada"
        return "Alerta {} para evento {}".format(enabled, EVENTOS_DICT[self.evento])


# Tipos de alerta:
#    - Sale una empresa a la que está suscrita (suscripción por empresa)
#    - Sale una persona a la que está suscrito (suscripción por persona)
#    - Sale algún acto mercantil al que se está suscrito (suscripción por acto)
#        - En liquidación
#        - Concurso de acreedores
