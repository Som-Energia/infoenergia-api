import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

import unittest
from concurrent import futures
from unittest import TestCase, skip, mock

import yaml
from api import app
from api.registration.models import User
from passlib.hash import pbkdf2_sha256
from pony.orm import db_session, commit
from sanic.log import logger
from sanic_jwt.authentication import Authentication

import api.tasks


with open(os.path.join(app.config.BASE_DIR, 'tests/json4test.yaml')) as f:
    json4test = yaml.load(f.read())


class BaseTestCace(TestCase):

    def setUp(self):
        self.client = app.test_client
        self.maxDiff = None
        if app.thread_pool._shutdown:
            APP.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)

    @db_session
    def get_or_create_user(self, username, password, email, partner_id, is_superuser):
        user = User.get(username=username)
        if not user:
            user = User(
                username=username,
                password=pbkdf2_sha256.hash(password),
                email=email,
                id_partner=partner_id,
                is_superuser=is_superuser
            )
            commit()
        return user

    @db_session
    def delete_user(self, user):
        user.delete()

    @db_session
    def get_auth_token(self, username, password):
        auth_body = {
            'username': username,
            'password': password,
        }
        request, response = self.client.post('/auth', json=auth_body)
        token = response.json.get('access_token', None)
        return token


class TestF1Base(BaseTestCace):

    @mock.patch('api.f1_measures.f1_measures.async_get_invoices')
    @db_session
    def test__get_f1_by_contracts_id(self, async_get_invoices_mock):
        async_get_invoices_mock.return_value = json4test['f1_contract_id']['invoices']
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")

        request, response = self.client.get(
            '/f1/' + json4test['f1_contract_id']['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertListEqual(
            response.json,
            json4test['f1_contract_id']['contract_data']
        )
        self.delete_user(user)

    @mock.patch('api.f1_measures.f1_measures.async_get_invoices')
    @db_session
    def test__get_f1_measures(self, async_get_invoices_mock):
        async_get_invoices_mock.return_value = json4test['f1_contracts']['invoices']
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")

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
            json4test['f1_contracts']['contract_data']

        )
        self.delete_user(user)
