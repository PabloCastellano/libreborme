# PRIVATE
import csv
import logging
import requests

from lxml import html

from django.utils.text import slugify
from borme.models import Company

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('nif')
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

    @property
    def is_slug(self):
        return self.company == slugify(self.company)

    def _get_content_and_xpath(self, url, xpath, provider):
        logger.debug(url)
        page = requests.get(url, allow_redirects=True, headers=self.headers)
        logger.debug(page.status_code)

        # Works for: infoempresa
        if page.status_code == 404:
            raise NIFNotFoundException(self.company)

        tree = html.fromstring(page.content)
        try:
            title = tree.xpath('//title/text()')[0]
        except IndexError:
            raise NIFParserException("Error while parsing title in URL " + url)

        if (provider == 'empresia' and 'Resultados de búsqueda' in title) \
           or (provider == 'infocif' and 'Informacion Financiera' not in title):
            raise NIFNotFoundException(self.company)

        try:
            return tree.xpath(xpath)[0]
        except IndexError:
            raise NIFParserException("Error while parsing NIF in URL " + url)

    def _get_nif_infocif(self):
        nif = None
        xpath = "/html/body/div[1]/section/div/div[5]/div/div/div/div[4]/div[2]/div/div/div[1]/h2/text()"
        if self.is_slug:
            url = 'http://www.infocif.es/ficha-empresa/' + self.company
            nif = self._get_content_and_xpath(url, xpath, provider='infocif')
        else:
            self._search(self.company)
            # if len(results) == 1: save
            # else: don't save, report
        return nif

    def _get_nif_empresia(self):
        nif = None
        xpath = "/html/body/section/div[1]/div[3]/div[2]/div/div[1]/p/text()"
        if self.is_slug:
            url = 'https://www.empresia.es/empresa/' + self.company
            nif = self._get_content_and_xpath(url, xpath, provider='empresia')
        else:
            self._search(self.company)
        return nif

    def _get_nif_infoempresa(self):
        nif = None
        xpath = "/html/body/div[1]/div[2]/div/div/main/div/div/section[1]/div/div/dl/dd[3]/text()"
        if self.is_slug:
            url = 'https://www.infoempresa.com/es-es/es/empresa/' + self.company
            nif = self._get_content_and_xpath(url, xpath, provider='infoempresa')
        else:
            self._search(self.company)
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
            raise NotImplementedError
        return nif

    def get(self, provider=None):

        if provider:
            nif = self._get_nif_from_provider(provider)
        else:
            for provider in PROVIDERS:
                nif = self._get_nif_from_provider(provider)
                if nif:
                    break

        if not nif:
            logger.warning("Could not find NIF for company '{}'".format(self.company))
        elif not validate_nif(nif):
            raise NIFInvalidException(nif)

        return nif, provider

    def _search(self, company):
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
    nif = None
    created = False

    nif_provider = NIFProvider(company)
    nif, provider = nif_provider.get(provider=provider)

    if not nif:
        raise NIFNotFoundException(company)

    if save_to_db:
        slug = slugify(company)
        try:
            c = Company.objects.get(slug=slug)
        except Company.DoesNotExist:
            logger.warning("Company {} doesn't exist in DB, hence not saving NIF".format(slug))
            return nif, created

        if c.nif:
            if c.nif == nif:
                logger.debug("NIF for Company '{}' already exists in DB.".format(company))
            else:
                logger.error("NIF for Company '{}' in DB [{}] is different from found [{}]".format(company, c.nif, nif))
        else:
            created = True
            c.nif = nif
            c.save()
            logger.debug("NIF for Company '{}' saved [{}]".format(company, nif))

    if created:
        logger.debug("Got NIF '{}' for '{}' using provider '{}'".format(nif, company, provider))

    return nif, created, provider


def export(filename):
    companies = Company.objects.filter(nif__isnull=False).order_by('name')

    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Name", "Slug", "NIF"])
        for company in companies:
            csvwriter.writerow([company.name, company.slug, company.nif])

    return len(companies)
