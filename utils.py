from django.contrib.auth.models import User

from .models import AlertasConfig, Profile


def get_alertas_config(key=None):
    if key:
        return AlertasConfig.objects.get(key=key).value
    else:
        alertas = {}
        for alerta in AlertasConfig.objects.all():
            alertas[alerta.key] = alerta.value
        return alertas


def create_alertas_user(username, email, password, first_name, last_name, type):
    new_user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
    profile = Profile(user=new_user, account_type=type, notification_email=email)
    profile.save()
    return new_user
