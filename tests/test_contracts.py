import os
import unittest
from unittest import TestCase

import yaml
from api import app


class TestContracts(TestCase):

    def setUp(self):
        self.client = app.test_client
        self.maxDiff = None

    def get_auth_token(self, username, password):
        auth_body = {
            'username': username,
            'password': password
        }

        request, response = self.client.post('/auth', json=auth_body)
        token = response.json.get('access_token', None)
        return token

    @db_session
    def test__get_contracts_by_id(self):
        user = User(
            username='Joaquina',
            password=pbkdf2_sha256.hash("12341234"),
            id_partner=1,
            is_superuser=True
        )
        token = self.get_auth_token('Joaquina', '12341234')

        request, response = self.client.get(
            '/contracts/'+json4test['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            json4test['jsonContractById']
        )
        user.delete()

    @db_session
    def test__get_contracts___auth_user(self):
        user = User(
            username='Joaquina',
            password=pbkdf2_sha256.hash("12341234"),
            id_partner=1,
            is_superuser=True
        )
        token = self.get_auth_token('Joaquina', '12341234')

        params = {
            'from_': '2019-10-03',
            'to_': '2019-10-09',
            'tariff': '2.0DHS',
            'juridic_type': 'physical_person',
        }
        request, response = self.client.get(
            '/contracts',
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )

        self.assertEqual(response.status, 200)
        self.assertListEqual(
            response.json,
            json4test['jsonList']

        )
        user.delete()
