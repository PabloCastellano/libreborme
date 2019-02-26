import json

from alertas.models import EVENTOS_DICT, SubscriptionEvent
from libreborme.provincias import PROVINCIAS_CODE_DICT as PROVINCIA

SUPPORTED_VERSION = "3"


def import_subscription_event(source):
    """Importa un archivo con resultados de SubscriptionEvent en la BD.

    :param filename: Archivo a importar
    :type filename: str or file
    :param evento: Tipo de evento
    :type evento: str
    """

    if isinstance(source, dict):
        content = source
    else:
        print("Importing " + source)
        with open(source) as fp:
            content = json.load(fp)

    if content["version"] != SUPPORTED_VERSION:
        raise ValueError("Version {} != {}".format(
            content["version"], SUPPORTED_VERSION)
        )

    if content["event"] not in EVENTOS_DICT.keys():
        raise ValueError("Unknown event: {}".format(content["event"]))

    try:
        subscription_event = SubscriptionEvent.objects.get(
            province=PROVINCIA[content["provincia"]],
            event=content["event"],
            event_date=content["date"],
        )
        subscription_event.delete()
    except SubscriptionEvent.DoesNotExist:
        pass
    finally:
        SubscriptionEvent.objects.create(
            province=PROVINCIA[content["provincia"]],
            event=content["event"],
            event_date=content["date"],
            data_json=content["results"]
        )
