#!/usr/bin/env python3
import json
import logging
import sys

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FILE_VERSION = "1"


def _parse_subscription_adm(content):
    results = {}
    for page in content['pages']:
        for announcement in page:
            new_admin = False
            admins = []
            for act in announcement['announcements']:
                if act['label'] == 'Nombramientos':
                    for role in act['roles']:
                        # Hacky
                        if 'adm' in role[0].lower():
                            new_admin = True
                            admins.append(role)
            if new_admin:
                for role in admins:
                    # print("{} tiene nombramiento de {}: {}".format(announcement['company'], role[0], role[1]))
                    results.setdefault(announcement['company'], [])
                    results[announcement['company']].append([role[0], role[1]])
    return results


def parse_borme_json(event, filename):
    logger.debug("Parsing " + filename)

    # TODO: Check yabormeparser file

    with open(filename) as fp:
        content = json.load(fp)

    if event == "adm":
        results = _parse_subscription_adm(content)
    else:
        raise NotImplementedError(event)

    output = {
        "cve": content["cve"],
        "date": content["publish_date"],
        "event": event,
        "provincia": content["provincia"],
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
        json.dump(results, sys.stdout, sort_keys=True, indent=4)
        # print("Writing " + output_filename)
        # with open(output_filename, "w") as fp:
        #     json.dump(results, fp, sort_keys=True, indent=4)
