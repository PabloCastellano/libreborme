import json

from alertas.models import EVENTOS_DICT, SubscriptionEvent
from libreborme.provincias import PROVINCIAS_CODE_DICT as PROVINCIA

SUPPORTED_VERSION = "2"


def from_dict(content):
    if content["version"] != SUPPORTED_VERSION:
        raise ValueError("Version {} != {}".format(
            content["version"], SUPPORTED_VERSION)
        )

    if content["event"] not in EVENTOS_DICT.keys():
        raise ValueError("Unknown event: {}".format(content["event"]))

    already_exists = SubscriptionEvent.objects.filter(
        province=PROVINCIA[content["provincia"]],
        event=content["event"],
        event_date=content["date"],
    ).exists()

    if already_exists:
        print("Already exists")
    else:
        SubscriptionEvent.objects.create(
            province=PROVINCIA[content["provincia"]],
            event=content["event"],
            event_date=content["date"],
            data_json=content["results"]
        )
        print("OK")


def from_json_file(filename):
    """Importa un archivo con resultados de SubscriptionEvent en la BD.

    :param filename: Archivo a importar
    :type filename: str or file
    :param evento: Tipo de evento
    :type evento: str
    """

    print("Importing " + filename)

    with open(filename) as fp:
        content = json.load(fp)

    from_dict(content)
