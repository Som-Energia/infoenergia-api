from unittest import mock

from pony.orm import db_session

from tests.base import BaseTestCase


class TestF1Base(BaseTestCase):

    @mock.patch('infoenergia_api.api.f1_measures.f1_measures.async_get_invoices')
    @db_session
    def test__get_f1_by_contracts_id(self, async_get_invoices_mock):
        async_get_invoices_mock.return_value = self.json4test['f1_contract_id']['invoices']
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")

        _, response = self.client.get(
            '/f1/' + self.json4test['f1_contract_id']['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertListEqual(
            response.json,
            self.json4test['f1_contract_id']['contract_data']
        )
        self.delete_user(user)

    @mock.patch('infoenergia_api.api.f1_measures.f1_measures.async_get_invoices')
    @db_session
    def test__get_f1_measures(self, async_get_invoices_mock):
        async_get_invoices_mock.return_value = self.json4test['f1_contracts']['invoices']
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

        _, response = self.client.get(
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
            self.json4test['f1_contracts']['contract_data']

        )
        self.delete_user(user)
