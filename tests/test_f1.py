import os
import unittest
from concurrent import futures
from unittest import TestCase, skip

import yaml
from api import app
from api.registration.models import User
from passlib.hash import pbkdf2_sha256
from pony.orm import db_session
from sanic.log import logger
from sanic_jwt.authentication import Authentication

os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')


with open(os.path.join(app.config.BASE_DIR, 'tests/json4test.yaml')) as f:
    json4test = yaml.load(f.read())


class BaseTestCace(TestCase):

    def setUp(self):
        self.client = app.test_client
        self.maxDiff = None
        if app.thread_pool._shutdown:
            app.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)


class TestF1Base(BaseTestCace):
    @db_session
    def test__get_f1_by_contracts_id(self):
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
            '/f1/' + json4test['contractId2F1'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertListEqual(
            response.json,
            json4test['jsonF1_contractID']
        )
        user.delete()

    @db_session
    def test__get_f1_measures(self):
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
            'from_': '2019-09-01',
            'to_': '2019-09-01',
            'tariff': '3.1A',
        }
        request, response = self.client.get(
            '/f1',
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertListEqual(
            response.json,
            json4test['jsonF1']

        )
        user.delete()
