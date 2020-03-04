import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

from passlib.hash import pbkdf2_sha256
from pony.orm import db_session

from api.registration.models import User

from .base import BaseTestCase


class TestContracts(BaseTestCase):

    @db_session
    def test__get_contracts_by_id__2A(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")
        _, response = self.client.get(
            '/contracts/' + self.json4test['contract_id_2A']['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            self.json4test['contract_id_2A']['contract_data']
        )
        self.delete_user(user)

    @db_session
    def test__get_contracts__20DHS(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2019-10-03',
            'to_': '2019-10-09',
            'tariff': '2.0DHS',
            'juridic_type': 'physical_person',
        }
        _, response = self.client.get(
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
            self.json4test['contracts_20DHS']['contract_data']

        )
        self.delete_user(user)

