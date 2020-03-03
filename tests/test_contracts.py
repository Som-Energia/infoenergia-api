import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

import unittest
from concurrent import futures
from unittest import TestCase, skip

import yaml
from passlib.hash import pbkdf2_sha256
from pony.orm import db_session
from sanic.log import logger
from sanic_jwt.authentication import Authentication

from api import app
from api.registration.models import User


with open(os.path.join(app.config.BASE_DIR, 'tests/json4test.yaml')) as f:
    json4test = yaml.load(f.read())


class BaseTestCace(TestCase):

    def setUp(self):
        self.client = app.test_client
        self.maxDiff = None
        if app.thread_pool._shutdown:
            app.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)


class TestLogin(BaseTestCace):

    @db_session
    def test__authenticate_user(self):
        user = User(
            username='someone',
            password=pbkdf2_sha256.hash("12341234"),
            email='someone@somenergia.coop',
            id_partner=1,
            is_superuser=True
        )
        auth_body = {
            'username': user.username,
            'password': "12341234",
            'email': user.email
        }

        request, response = self.client.post('/auth', json=auth_body)
        token = response.json.get('access_token', None)

        self.assertIsNotNone(token)

        user.delete()


class TestContracts(BaseTestCace):

    @db_session
    def test__get_contracts_by_id(self):
        # TODO: Delete this
        def get_auth_token(username, password, email):
            auth_body = {
                'username': username,
                'password': password,
                'email': email
            }
            request, response = self.client.post('/auth', json=auth_body)
            token = response.json.get('access_token', None)
            return token

        user = User(
            username='someone',
            password=pbkdf2_sha256.hash("123412345"),
            email='someone@somenergia.coop',
            id_partner=1,
            is_superuser=True
        )
        token = get_auth_token(
            'someone',
            '123412345',
            'someone@somenergia.coop'
        )
        request, response = self.client.get(
            '/contracts/' + json4test['contractId2A'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            json4test['jsonContractById2A']
        )
        user.delete()

    @db_session
    def test__get_contracts___auth_user(self):
        # TODO: Delete this
        def get_auth_token(username, password, email):
            auth_body = {
                'username': username,
                'password': password,
                'email': email
            }
            request, response = self.client.post('/auth', json=auth_body)
            token = response.json.get('access_token', None)
            return token

        user = User(
            username='someone',
            password=pbkdf2_sha256.hash("123412345"),
            email='someone@somenergia.coop',
            id_partner=1,
            is_superuser=True
        )
        token = get_auth_token(
            'someone',
            '123412345',
            'someone@somenergia.coop'
        )
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
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertListEqual(
            response.json,
            json4test['jsonList']

        )
        user.delete()
