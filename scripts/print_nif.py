#!/usr/bin/env python3
#
# ./manage.py runscript print_nif
#
# Hay otra forma casi compatible:
# ./manage.py shell < print_nif.py
#
import datetime
from tabulate import tabulate
from borme.models import Company


def run():
    companies = Company.objects.filter(date_updated=datetime.date(2019,1,17))
    print("Found {} companies".format(len(companies)))
    l = []
    for c in companies:
        l.append([c.fullname, c.nif or ""])
    print(tabulate(l, headers=["Name", "NIF"]))
