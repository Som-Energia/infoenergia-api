#!/usr/bin/env python
# -*- coding: utf-8 -*-

from passlib.hash import pbkdf2_sha256
from pony.orm import db_session

from tests.base import BaseTestCase


class TestModContracts(BaseTestCase):

    @db_session
    def test__get_modcontracts__canceled(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2019-09-17',
            'to_': '2019-09-17',
            'type': 'canceled',
        }
        _, response = self.client.get(
            '/modcontracts',
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'total_results': 2,
                'count': 2,
                'data': self.json4test['contracts_canceled']['contract_data']
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_modcontracts__tariffOrPower(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2019-10-19',
            'to_': '2019-10-19',
            'type': 'tariff_power',
        }
        _, response = self.client.get(
            '/modcontracts',
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'total_results': 1,
                'count': 1,
                'data': self.json4test['contracts_mod_tariff_power']['contract_data']
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_modcontracts__without_permission(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=False,
            category='Energética'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2019-10-19',
            'to_': '2019-10-19',
            'type': 'tariff_power',
        }
        _, response = self.client.get(
            '/modcontracts',
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'total_results': 0,
                'count': 0,
                'data': []
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_modcontracts__by_contract(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2000-10-01',
            'to_': '2019-10-19',
        }
        _, response = self.client.get(
            '/modcontracts/' + self.json4test['modcontract_by_id']['contractId'],
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'total_results': 1,
                'count': 1,
                'data': self.json4test['modcontract_by_id']['contract_data']
            }
        )
        self.delete_user(user)
