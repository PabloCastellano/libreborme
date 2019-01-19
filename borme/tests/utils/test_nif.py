# PRIVATE
from django.test import TestCase
from django.utils import timezone

import datetime
import gzip
from pathlib import Path
import responses

from borme.models import Company
import libreborme.nif

FIXTURES_PATH = Path(__file__).parent.parent / 'fixtures'


def get_fixture(filename):
    fullname = filename + '.html.gz'
    filepath = FIXTURES_PATH / fullname
    fp = gzip.open(str(filepath))
    content = fp.read()
    fp.close()
    return content


class TestNIFUtils(TestCase):

    def setUp(self):
        self.company1 = Company.objects.create(name="Endesa S.A", date_updated=datetime.date(2018, 1, 2))
        self.company2 = Company.objects.create(name="Company 404 S.A", date_updated=datetime.date(2018, 1, 2))
        self.provider = libreborme.nif.NIFProvider(company=self.company1)

    @responses.activate
    def test_nifprovider(self):
        responses.add(responses.GET,
                      'https://www.empresia.es/empresa/endesa',
                      body=get_fixture('empresia-endesa'),
                      status=200)
        responses.add(responses.GET,
                      'http://www.infocif.es/ficha-empresa/endesa-sa',
                      body=get_fixture('infocif-endesa'),
                      status=200)
        responses.add(responses.GET,
                      'https://www.infoempresa.com/es-es/es/empresa/endesa-sa',
                      body=get_fixture('infoempresa-endesa'),
                      status=200)

        self.assertEqual(self.provider.company, self.company1)

        # any provider
        nif, provider = self.provider.get_from_any_provider()
        self.assertEqual(nif, 'A28023430')
        self.assertEqual(provider, 'empresia')

        nif = self.provider.get(provider='infocif')
        self.assertEqual(nif, 'A28023430')

        nif = self.provider.get(provider='infoempresa')
        self.assertEqual(nif, 'A28023430')

        nif = self.provider.get(provider='empresia')
        self.assertEqual(nif, 'A28023430')

    @responses.activate
    def test_find_nif(self):
        responses.add(responses.GET,
                      'https://www.empresia.es/empresa/endesa',
                      body=get_fixture('empresia-endesa'),
                      status=200)
        responses.add(responses.GET,
                      'https://www.infoempresa.com/es-es/es/empresa/company-404-sa',
                      status=404)

        nif, created, provider = libreborme.nif.find_nif(self.company1)
        self.assertEqual(nif, 'A28023430')
        self.assertEqual(created, True)
        self.assertEqual(provider, 'empresia')

        # Run second time
        nif, created, provider = libreborme.nif.find_nif(self.company1)
        self.assertEqual(nif, 'A28023430')
        self.assertEqual(created, False)
        self.assertEqual(provider, 'empresia')

        with self.assertRaises(libreborme.nif.NIFNotFoundException):
            libreborme.nif.find_nif(self.company2, provider='infoempresa')

        # TODO: test NIFParserException and save_to_db parameter

    def test_validate_nif(self):
        # valid company NIF
        is_valid = libreborme.nif.validate_nif('A28023430')
        self.assertEqual(is_valid, True)

        # valid person NIF
        is_valid = libreborme.nif.validate_nif('00000014Z')
        self.assertEqual(is_valid, True)

        # invalid NIF (incorrect length)
        is_valid = libreborme.nif.validate_nif('123')
        self.assertEqual(is_valid, False)

        # invalid NIF (incorrect format)
        is_valid = libreborme.nif.validate_nif('000000141')
        self.assertEqual(is_valid, False)
