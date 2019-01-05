# PRIVATE
from django.test import TestCase
from django.utils import timezone

import gzip
from pathlib import Path
import responses

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
        self.provider = libreborme.nif.NIFProvider(company='endesa-sa')
        self.provider2 = libreborme.nif.NIFProvider(company='endesa')

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

        self.assertEqual(self.provider.company, 'endesa-sa')
        self.assertEqual(self.provider.is_slug, True)

        # any provider
        nif = self.provider.get()
        self.assertEqual(nif, 'A28023430')

        nif = self.provider.get(provider='infocif')
        self.assertEqual(nif, 'A28023430')

        nif = self.provider.get(provider='infoempresa')
        self.assertEqual(nif, 'A28023430')

        nif = self.provider2.get(provider='empresia')
        self.assertEqual(nif, 'A28023430')

    @responses.activate
    def test_find_nif(self):
        responses.add(responses.GET,
                      'http://www.infocif.es/ficha-empresa/endesa-sa',
                      body=get_fixture('infocif-endesa'),
                      status=200)
        responses.add(responses.GET,
                      'https://www.infoempresa.com/es-es/es/empresa/endesa',
                      status=404)

        nif = libreborme.nif.find_nif('endesa-sa')
        self.assertEqual(nif, 'A28023430')

        with self.assertRaises(libreborme.nif.NIFNotFoundException):
            libreborme.nif.find_nif('endesa', provider='infoempresa')

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
