from django.conf import settings
from django.template.loader import get_template

from .models import CompanyRobotsTxt, PersonRobotsTxt

import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def regenerate_robotstxt(print_output=False):
    companies = CompanyRobotsTxt.objects.order_by('company__slug')
    persons = PersonRobotsTxt.objects.order_by('person__slug')

    template = get_template("robots_template.txt")
    parameters = {
        "companies": companies,
        "persons": persons,
    }
    response = template.render(parameters)
    if print_output:
        print(response)

    static_root = settings.STATIC_ROOT
    if static_root is None:
        logger.warn("STATIC_ROOT is not defined. Using /tmp")
        static_root = "/tmp"
    filename = Path(static_root) / "robots.txt"
    filename = filename.as_posix()
    with open(filename, "w") as fp:
        fp.write(response)

    results = {
        "path": filename,
        "companies": len(companies),
        "persons": len(persons)
    }
    return results
