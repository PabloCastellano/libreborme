from .models import AlertasConfig


def get_alertas_config():
    alertas = {}
    for alerta in AlertasConfig.objects.all():
        alertas[alerta.key] = alerta.value
    return alertas
