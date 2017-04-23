from django.apps import apps
from django.contrib.auth.models import User


def get_alertas_config(key=None):
    AlertasConfig = apps.get_model("alertas", "AlertasConfig")

    if key:
        return AlertasConfig.objects.get(key=key).value
    else:
        alertas = {}
        for alerta in AlertasConfig.objects.all():
            alertas[alerta.key] = alerta.value
        return alertas


def create_alertas_user(username, email, password, first_name, last_name, type):
    Profile = apps.get_model("alertas", "Profile")

    new_user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
    profile = Profile(user=new_user, account_type=type, notification_email=email)
    profile.save()
    return new_user


def insert_libreborme_log(component, log, user=None):
    LibrebormeLogs = apps.get_model("alertas", "LibrebormeLogs")

    log = LibrebormeLogs(component=component, log=log, user=user)
    log.save()
