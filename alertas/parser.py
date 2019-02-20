#!/usr/bin/env python3
import io
import json
import logging
import sys

from borme.models import Company

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FILE_VERSION = "3"


def is_administrador(position):
    # FIXME: Hacky
    return 'adm' in position.lower()


def _parse_subscription_adm(content):
    results = []
    for page in content['pages']:
        for announcement in page:
            new_admin = False
            constitucion = False
            datos_registrales = ""
            admins = []
            for act in announcement['announcements']:
                if act['label'] == 'Nombramientos':
                    for role in act['roles']:
                        if is_administrador(role[0]):
                            new_admin = True
                            admins.append(role)
                elif act['label'] == 'Datos registrales':
                    datos_registrales = act['datos_registrales']
                elif act['label'] == 'Constitución':
                    constitucion = True
            if new_admin and not constitucion:
                logger.debug(announcement['company'])
                try:
                    company = Company.objects.get(name=announcement['company'])
                    company_dict = {
                        "company": {
                            "name": company.name,
                            "nif": company.nif or "",
                            "address": company.domicilio or "",
                            "url_web": "https://libreborme.net" + company.get_absolute_url(),
                            "url_api": "https://api.libreborme.net/v1/empresa/{}".format(company.slug),
                        },
                        "datos_registrales": datos_registrales,
                        "new_roles": [],
                    }

                    if company.date_creation:
                        company_dict["company"]["date_creation"] = company.date_creation.isoformat()

                    for role in admins:
                        # print("{} tiene nombramiento de {}: {}".format(announcement['company'], role[0], role[1]))
                        company_dict["new_roles"].append([role[0], role[1]])
                    results.append(company_dict)
                except Company.DoesNotExist:
                    logger.error("Company '{}' not found while generating subscriptions (adm)".format(announcement['company']))
    return results


def parse_borme_json(event, filename):
    """
    event: EVENT_DICT
    filename: str or fp
    """

    if isinstance(filename, io.IOBase):
        content = filename.read().decode('utf-8')
        document = json.loads(content)
    else:
        logger.debug("Parsing " + filename)
        with open(filename) as fp:
            document = json.load(fp)

    # TODO: Check yabormeparser file

    if event == "adm":
        results = _parse_subscription_adm(document)
    else:
        raise NotImplementedError(event)

    output = {
        "cve": document["cve"],
        "date": document["publish_date"],
        "event": event,
        "provincia": document["provincia"],
        "results": results,
        "version": FILE_VERSION,
    }
    return output


def usage():
    print("Usage: {} <liq|new|adm> <path...>".format(sys.argv[0]))


if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
    else:
        event, filename = sys.argv[1], sys.argv[2]
        results = parse_file(event, filename)
        # print_simple(results)
        borme = results["cve"]
        output_filename = borme + "_" + event + ".json"
        json.dump(results, sys.stdout, sort_keys=True, indent=4, ensure_ascii=False)
        # print("Writing " + output_filename)
        # with open(output_filename, "w") as fp:
        #     json.dump(results, fp, sort_keys=True, indent=4)
