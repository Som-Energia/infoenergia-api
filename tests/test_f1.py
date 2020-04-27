from unittest import mock

from pony.orm import db_session

from infoenergia_api.contrib import Invoice, InvoiceList, get_invoices

from tests.base import BaseTestCase


class TestF1Base(BaseTestCase):

    @mock.patch('infoenergia_api.api.f1_measures.f1_measures.async_get_invoices')
    @db_session
    def test__get_f1_measures_by_contract_id(self, async_get_invoices_mock):
        async_get_invoices_mock.return_value = InvoiceList(self.json4test['invoices_f1_by_contract_id'])
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")

        request, response = self.client.get(
            '/f1/' + self.json4test['invoices_f1_by_contract_id']['contractId'],
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
        async_get_invoices_mock.return_value = InvoiceList(self.json4test['invoices_f1'])
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
            self.json4test['f1_contracts']['contract_data']

        )
        async_get_invoices_mock.assert_called_with(request)
        self.delete_user(user)


class TestInvoice(BaseTestCase):

    invoice_id_2x = 8174595
    invoice_id_3x = 8119604

    def test__create_invoice(self):
        invoice = Invoice(self.invoice_id_2x)

        self.assertIsInstance(invoice, Invoice)

    def test__get_devices(self):
        invoice = Invoice(self.invoice_id_2x)

        devices = invoice.devices
        self.assertListEqual(
            devices,
            [
                {
                    'dateStart': '2011-12-23T00:00:00-00:15Z',
                    'dateEnd': None,
                    'deviceId': 'ab201f66-4da7-517b-be40-13b7e0de7429'
                }
            ]
        )

    def test__f1_power_2X(self):
        invoice = Invoice(self.invoice_id_2x)

        f1_power = invoice.f1_power_kW
        self.assertListEqual(
            f1_power, []
        )

    def test__f1_power_3X(self):
        invoice = Invoice(self.invoice_id_3x)

        f1_power = invoice.f1_power_kW
        self.assertListEqual(
            f1_power,
            [
                {'excess': 0.0, 'maximeter': 29.0, 'period': 'P1', 'units': 'kW'},
                {'excess': 0.0, 'maximeter': 12.0, 'period': 'P2', 'units': 'kW'},
                {'excess': 0.0, 'maximeter': 3.0, 'period': 'P3', 'units': 'kW'},
                {'excess': 0.0, 'maximeter': 25.0, 'period': 'P4', 'units': 'kW'},
                {'excess': 0.0, 'maximeter': 26.0, 'period': 'P5', 'units': 'kW'},
                {'excess': 0.0, 'maximeter': 15.0, 'period': 'P6', 'units': 'kW'}
            ],
        )

    def test__get_f1_reactive_energy_2X(self):
        invoice = Invoice(self.invoice_id_2x)

        f1_reactive_energy = invoice.f1_reactive_energy_kVArh
        self.assertListEqual(
            f1_reactive_energy, []
        )

    def test__get_f1_reactive_energy_3X(self):
        invoice = Invoice(self.invoice_id_3x)

        f1_reactive_energy = invoice.f1_reactive_energy_kVArh
        self.assertListEqual(
            f1_reactive_energy,
            [
                {'consum': 41, 'period': 'P1', 'source': 'TPL', 'units': 'kVArh'},
                {'consum': 13, 'period': 'P2', 'source': 'TPL', 'units': 'kVArh'},
                {'consum': 0, 'period': 'P3', 'source': 'TPL', 'units': 'kVArh'},
                {'consum': 11, 'period': 'P4', 'source': 'TPL', 'units': 'kVArh'},
                {'consum': 24, 'period': 'P5', 'source': 'TPL', 'units': 'kVArh'},
                {'consum': 46, 'period': 'P6', 'source': 'TPL', 'units': 'kVArh'}
            ]
        )

    def test__get_f1_active_energy_2X(self):
        invoice = Invoice(self.invoice_id_2x)

        f1_reactive_energy = invoice.f1_active_energy_kWh
        self.assertListEqual(
            f1_reactive_energy,
            [{'consum': 280, 'period': 'P1', 'source': 'Telegestió', 'units': 'kWh'}]
        )

    def test__get_f1_active_energy_3X(self):
        invoice = Invoice(self.invoice_id_3x)

        f1_reactive_energy = invoice.f1_active_energy_kWh
        self.assertListEqual(
            f1_reactive_energy,
            [
                {'consum': 307, 'period': 'P1', 'source': 'TPL', 'units': 'kWh'},
                {'consum': 324, 'period': 'P2', 'source': 'TPL', 'units': 'kWh'},
                {'consum': 113, 'period': 'P3', 'source': 'TPL', 'units': 'kWh'},
                {'consum': 94, 'period': 'P4', 'source': 'TPL', 'units': 'kWh'},
                {'consum': 209, 'period': 'P5', 'source': 'TPL', 'units': 'kWh'},
                {'consum': 212, 'period': 'P6', 'source': 'TPL', 'units': 'kWh'}
            ]
        )

    def test_f1_measures_2x(self):
        invoice = Invoice(self.invoice_id_2x)

        f1_measures = invoice.f1_measures

        self.assertDictEqual(f1_measures, self.json4test['invoices_f1_by_contract_id']['contract_data'][0])


class TestInvoiceList(BaseTestCase):

    def test__create_invoice_list(self):
        invoice_list = InvoiceList([8174595, 7568406])

        self.assertIsInstance(invoice_list, InvoiceList)

    def test__create_invoice_list(self):
        invoice_list = InvoiceList([8174595, 7568406])

        for invoice in invoice_list:
            self.assertIsInstance(invoice, Invoice)
