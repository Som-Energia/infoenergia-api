from unittest import TestCase
from api import app


class TestContracts(TestCase):

    def setUp(self):
        self.client = app.test_client
        self.maxDiff = 0

    def test__get_contracts(self):
        request, response = self.client.get('/contracts')

        self.assertEqual(response.status, 200)
        self.assertDictEqual(response.json, {'hola': 'caracola'})
