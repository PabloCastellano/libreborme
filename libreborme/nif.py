# PRIVATE
import csv
import logging
import requests

from lxml import html

from django.utils.text import slugify
from borme.models import Company

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


PROVIDERS = ('empresia', 'infocif', 'infoempresa')


class NIFException(Exception):
    """ Base class exception for problems while getting company NIF """
    pass


class NIFNotFoundException(NIFException):
    """ Exception raised when company NIF is not found """
    pass


class NIFParserException(NIFException):
    """ Exception raised when there is a problem while parsing NIF """
    pass


class NIFInvalidException(NIFException):
    """ Exception raised when NIF is invalid """
    pass


class NIFProvider(object):
    """ Get company NIF from other sources """

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

    def __init__(self, company):
        self.company = company

    def _check_page_title(self, title, provider):
        found = False
        if (provider == 'empresia' and 'Resultados de búsqueda' not in title):
            found = True
        elif (provider == 'infocif' and 'Informacion Financiera' in title):
            found = True
        elif (provider == 'infocif' and 'Informe comercial' in title):
            found = True

        if not found:
            raise NIFNotFoundException(self.company.fullname)

    def _get_content_and_xpath(self, url, xpath, provider):
        logger.debug(url)
        page = requests.get(url, allow_redirects=True, headers=self.headers)
        logger.debug(page.status_code)

        # Works for: infoempresa
        if page.status_code == 404:
            raise NIFNotFoundException(self.company.fullname)

        tree = html.fromstring(page.content)
        try:
            title = tree.xpath('//title/text()')[0]
        except IndexError:
            raise NIFParserException("Error while parsing title in URL " + url)

        self._check_page_title(title, provider)

        try:
            return tree.xpath(xpath)[0]
        except IndexError:
            raise NIFParserException("Error while parsing NIF in URL " + url)

    def _get_nif_infocif(self):
        xpath = "/html/body/div[1]/section/div/div[5]/div/div/div/div[4]/div[2]/div/div/div[1]/h2/text()"
        slug2 = slugify(self.company.fullname)

        url = 'http://www.infocif.es/ficha-empresa/' + slug2
        nif = self._get_content_and_xpath(url, xpath, provider='infocif')
        return nif

    def _get_nif_empresia(self):
        xpath = "/html/body/section/div[1]/div[3]/div[2]/div/div[1]/p/text()"

        url = 'https://www.empresia.es/empresa/' + self.company.slug
        nif = self._get_content_and_xpath(url, xpath, provider='empresia')
        return nif

    def _get_nif_infoempresa(self):
        xpath = "/html/body/div[1]/div[2]/div/div/main/div/div/section[1]/div/div/dl/dd[3]/text()"
        # TODO: & is also converted to - leading to double hyphens together
        slug2 = slugify(self.company.fullname)

        url = 'https://www.infoempresa.com/es-es/es/empresa/' + slug2
        nif = self._get_content_and_xpath(url, xpath, provider='infoempresa')
        return nif

    def _get_nif_from_provider(self, provider):
        logger.debug("Get using provider {}".format(provider))

        nif = None
        if provider == 'empresia':
            # No siempre vienen en empresia
            nif = self._get_nif_empresia()
        elif provider == 'infocif':
            nif = self._get_nif_infocif()
        elif provider == 'infoempresa':
            nif = self._get_nif_infoempresa()
        else:
            raise NotImplementedError(provider)
        return nif

    def validate_nif(self, nif):
        if not nif:
            logger.warning("Could not find NIF for company '{}'".format(self.company))
            raise NIFNotFoundException(self.company)
        elif not validate_nif(nif):
            raise NIFInvalidException(nif)

    def get(self, provider):
        if provider not in PROVIDERS:
            raise ValueError("Invalid provider: " + provider)

        nif = self._get_nif_from_provider(provider)
        self.validate_nif(nif)

        return nif

    def get_from_any_provider(self):
        nif = None
        for provider in PROVIDERS:
            try:
                nif = self._get_nif_from_provider(provider)
                self.validate_nif(nif)
                return nif, provider
            except NIFException as e:
                logger.error(e)

        raise NIFNotFoundException(self.company)

    def _search(self, provider):
        # if len(results) == 1: save
        # else: don't save, report
        raise NotImplementedError


def validate_nif(nif):
    """ Validate NIF """
    # TODO: Do real NIF validation
    if len(nif) == 9:
        # person
        if nif[0:8].isnumeric() and nif[8].isalpha():
            return True
        # company
        if nif[1:9].isnumeric() and nif[0].isalpha():
            return True
    return False


def find_nif(company, provider=None, save_to_db=True):
    """
    company: borme.models.Company
    """
    nif = None
    created = False

    nif_provider = NIFProvider(company)
    if provider:
        nif = nif_provider.get(provider=provider)
    else:
        nif, provider = nif_provider.get_from_any_provider()

    if save_to_db:

        if company.nif:
            if company.nif == nif:
                logger.debug("NIF for Company '{}' already exists in DB.".format(company))
            else:
                logger.error("NIF for Company '{}' in DB [{}] is different from found [{}]".format(company, company.nif, nif))
        else:
            created = True
            company.nif = nif
            company.save()
            logger.debug("NIF for Company '{}' saved [{}]".format(company, nif))

    if created:
        logger.debug("Got NIF '{}' for '{}' using provider '{}'".format(nif, company, provider))

    return nif, created, provider


def export_csv(filename):
    companies = Company.objects.filter(nif__isnull=False).order_by('name')

    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Name", "Slug", "NIF"])
        for company in companies:
            csvwriter.writerow([company.name, company.slug, company.nif])

    return len(companies)


def import_csv(filename):
    added = 0
    skipped = 0
    error = 0

    with open(filename) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            logger.debug(row["Slug"])
            try:
                company = Company.objects.get(slug=row["Slug"])
            except Company.DoesNotExist:
                logger.error("Company slug {} does not exist".format(row["Slug"]))
                error += 1
                continue

            if company.nif:
                if company.nif != row["NIF"]:
                    logger.error("NIF for Company '{}' in DB [{}] is different from found [{}]".format(company.slug, company.nif, row["NIF"]))
                    error += 1
                else:
                    skipped += 1
            else:
                if not validate_nif(nif):
                    logger.error("NIF '{}' for Company '{}' looks invalid".format(nif, company.slug))
                else:
                    company.nif = row["NIF"]
                    company.save()
                    added += 1

    return added, skipped, error
