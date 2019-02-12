from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model

from pathlib import Path

import datetime
import json

User = get_user_model()


def get_alertas_config(key=None):
    AlertasConfig = apps.get_model("alertas", "AlertasConfig")

    if key:
        return AlertasConfig.objects.get(key=key).value
    else:
        alertas = {}
        for alerta in AlertasConfig.objects.all():
            alertas[alerta.key] = alerta.value
        return alertas


def create_alertas_user(email, password,
                        first_name, last_name):
    new_user = User.objects.create_user(email=email,
                                        password=password,
                                        first_name=first_name,
                                        last_name=last_name)
    return new_user


def insert_libreborme_log(component, log, user=None):
    LibrebormeLogs = apps.get_model("alertas", "LibrebormeLogs")

    log = LibrebormeLogs(component=component, log=log, user=user)
    log.save()


def insert_alertas_history(user, type, date, entidad=None, provincia=None):
    """
        Insert new row in the AlertaHistory table

        user: User model object
        type: str
        date: datetime.date
        provincia = str
        entidad = str
    """
    AlertaHistory = apps.get_model("alertas", "AlertaHistory")
    alerta_history = AlertaHistory(user=user, type=type, date=date)

    if type in ("company", "person"):
        alerta_history.entidad = entidad
    else:
        # evento
        alerta_history.provincia = provincia

    alerta_history.save()
    return alerta_history


def get_subscription_data(evento, provincia, date=None):
    if not date:
        date = datetime.date.today()

    year = str(date.year)
    month = '{:02d}'.format(date.month)
    day = '{:02d}'.format(date.day)
    provincia = '{:02d}'.format(int(provincia))
    # filename = provincia + ".json"
    directory = Path(settings.BORME_SUBSCRIPTIONS_ROOT) / evento / year / month / day
    filename = (directory / (provincia + ".json")).as_posix()
    with open(filename) as fp:
        content = json.load(fp)
    return content
