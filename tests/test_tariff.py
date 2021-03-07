from unittest import mock, skip

from pony.orm import db_session

from infoenergia_api.contrib import TariffPrice, ReactiveEnergyPrice

from tests.base import BaseTestCase

class TestBaseTariff(BaseTestCase):

    def test__get_tariff_2A(self):
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
            'tariff': '2.0A',
        }
        _, response = self.client.get(
            '/tariff',
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
                'count': 7,
                'data': self.json4test['price2A']['data_AllPriceId']
            }
        )
        self.delete_user(user)

    def test__get_tariff__2A_with_priceId(self):
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
            'tariff': '2.0A',
            'tariffPriceId': 4
        }
        _, response = self.client.get(
            '/tariff',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            params=params,
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 1,
                'data': self.json4test['price2A']['data_OnePriceId']
            }
        )
        self.delete_user(user)


    def test__get_tariff__3A(self):
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
            'tariff': '3.0A',
        }
        _, response = self.client.get(
            '/tariff',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            params=params,
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 9,
                'data': self.json4test['price3A']['data']
            }
        )
        self.delete_user(user)

class TestTariff(BaseTestCase):

    tariff_id_2x = 4
    tariff_id_3x = 12
    tariff_id_3X_reactiva = 3
    items_id_2019_2X = [4955, 4956, 4959, 4960, 4957, 5318, 4958]
    items_id_2012_2X = [621, 622, 623, 624]
    items_id_2019_3X = [5057, 5058, 5059, 5060, 5061, 5062, 5066, 5067, 5068, 5069, 5063, 5064, 5324, 5325, 5326, 5065]
    items_id_reactiva = [572, 1524, 314, 1881, 457, 2125, 747, 3524, 93, 4472, 1222, 5220, 199, 5221, 94, 315, 458, 573, 200, 748, 1223, 1525, 1882, 2126, 3525, 4473]

    def test__create_tariff(self):
        tariff = TariffPrice(self.tariff_id_2x)

        self.assertIsInstance(tariff, TariffPrice)


    def test__get_active_energy_2019price2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2019_2X, 'ENERGIA', '€/kWh')

        self.assertEqual(energy, [{
            'period': 'P1',
            'price': 0.139,
            'units': '€/kWh'}]
        )


    def test__get_active_energy_2012price2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2012_2X, 'ENERGIA', '€/kWh')

        self.assertEqual(energy, [{
            'period': 'P1',
            'price': 0.144722,
            'units': '€/kWh'}]
        )


    def test__get_active_energy_price3X(self):
        tariff = TariffPrice(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, 'ENERGIA', 'kWh/day')

        self.assertEqual(energy, [
            {
                'period': 'P1',
                'price': 0.121,
                'units': 'kWh/day'
            },
            {
                'period': 'P2',
                'price': 0.105,
                'units': 'kWh/day'
            },
            {
                'period': 'P3',
                'price': 0.079,
                'units': 'kWh/day'
            },
            ]
        )


    def test__get_power_2019price2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2019_2X, 'POTENCIA', '€/kW year')

        self.assertEqual(energy, [{
            'period': 'P1',
            'price': 38.043426,
            'units': '€/kW year'}]
        )


    def test__get_power_2012price2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2012_2X, 'POTENCIA', '€/kW year')

        self.assertEqual(energy, [{
            'period': 'P1',
            'price': 19.893189,
            'units': '€/kW year'}]
        )


    def test__get_power_price3X(self):
        tariff = TariffPrice(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, 'POTENCIA', '€/kW year')

        self.assertEqual(energy, [
            {
                'period': 'P1',
                'price': 40.728885,
                'units': '€/kW year'
            },
            {
                'period': 'P2',
                'price': 24.43733,
                'units': '€/kW year'
            },
            {
                'period': 'P3',
                'price': 16.291555,
                'units': '€/kW year'
            },
            ]
        )


    def test__get_GkWh_2019price2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2019_2X, 'GKWh', '€/kWh')

        self.assertEqual(energy, [{
            'period': 'P1',
            'price': 0.116,
            'units': '€/kWh'}]
        )


    def test__get_GkWh_2012price2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2012_2X, 'GKWh', '€/kWh')

        self.assertEqual(energy, [])


    def test__get_GkWh_price3X(self):
        tariff = TariffPrice(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, 'GKWh', '€/kWh')

        self.assertEqual(energy, [
            {
                'period': 'P1',
                'price': 0.092,
                'units': '€/kWh'
            },
            {
                'period': 'P2',
                'price': 0.081,
                'units': '€/kWh'
            }
            ]
        )


    def test__get_tariff_historical_prices_2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        prices = tariff.priceDetail
        self.assertEqual(prices, self.json4test['price2A']['data_OnePriceId'][0]['price'])


    def test__get_reactive_energy(self):
        reactive_energy = ReactiveEnergyPrice.create().reactiveEnergy
        self.assertEqual(reactive_energy, self.json4test['reactiveEnergy'])


    def test__get_tariff_2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        tariff_json = tariff.tariff
        self.assertEqual(tariff_json, self.json4test['price2A']['data_OnePriceId'][0])
