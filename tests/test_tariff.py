from unittest import mock, skip

from pony.orm import db_session

from infoenergia_api.contrib import Tariff

from tests.base import BaseTestCase



class TestTariff(BaseTestCase):

    tariff_id_2x = 4
    tariff_id_3x = 12
    items_id_2019_2X = [4955, 4956, 4959, 4960, 4957, 5318, 4958]
    items_id_2019_3X = [5057, 5058, 5059, 5060, 5061, 5062, 5066, 5067, 5068, 5069, 5063, 5064, 5324, 5325, 5326, 5065]


    def test__create_tariff(self):
        tariff = Tariff(self.tariff_id_2x)

        self.assertIsInstance(tariff, Tariff)

    def test__get_active_energy_price2X(self):
        tariff = Tariff(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2019_2X, 'ENERGIA', 'kWh/day')

        self.assertEqual(energy, [{
            'name': 'P1_ENERGIA_20ASOM',
            'period': 'P1',
            'price': 0.139,
            'units': 'kWh/day'}]
        )

    def test__get_active_energy_price3X(self):
        tariff = Tariff(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, 'ENERGIA', 'kWh/day')

        self.assertEqual(energy, [
            {
                'name': 'P1_ENERGIA_3.0A',
                'period': 'P1',
                'price': 0.121,
                'units': 'kWh/day'
            },
            {
                'name': 'P2_ENERGIA_3.0A',
                'period': 'P2',
                'price': 0.105,
                'units': 'kWh/day'
            },
            {
                'name': 'P3_ENERGIA_3.0A',
                'period': 'P3',
                'price': 0.079,
                'units': 'kWh/day'
            },
            ]
        )

    def test__get_reactive_energy_price3X(self):
        tariff = Tariff(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, 'REACTIVA', 'kWh/day')

        self.assertEqual(energy,[
            {
                'name': 'P1_REACTIVA_3.0A',
                'period': 'P1',
                'price': 0.0,
                'units': 'kWh/day'
            },
            {
                'name': 'P2_REACTIVA_3.0A',
                'period': 'P2',
                'price': 0.0,
                'units': 'kWh/day'
            }
            ]
        )

    def test__get_reactive_energy_price2X(self):
        tariff = Tariff(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2019_2X, 'REACTIVA', 'kWh/day')

        self.assertEqual(energy, [{
            'name': 'P1_REACTIVA_20ASOM',
            'period': 'P1',
            'price': 0.0,
            'units': 'kWh/day'}]
        )

    def test__get_power_price2X(self):
        tariff = Tariff(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2019_2X, 'POTENCIA', 'kW/year')

        self.assertEqual(energy, [{
            'name': 'P1_POTENCIA_20ASOM',
            'period': 'P1',
            'price': 38.043426,
            'units': 'kW/year'}]
        )

    def test__get_power_price3X(self):
        tariff = Tariff(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, 'POTENCIA', 'kW/year')

        self.assertEqual(energy, [
            {
                'name': 'P1_POTENCIA_3.0A',
                'period': 'P1',
                'price': 40.728885,
                'units': 'kW/year'
            },
            {
                'name': 'P2_POTENCIA_3.0A',
                'period': 'P2',
                'price': 24.43733,
                'units': 'kW/year'
            },
            {
                'name': 'P3_POTENCIA_3.0A',
                'period': 'P3',
                'price': 16.291555,
                'units': 'kW/year'
            },
            ]
        )

    def test__get_GkWh_price2X(self):
        tariff = Tariff(self.tariff_id_2x)
        energy = tariff.termPrice(self.items_id_2019_2X, 'GKWh', 'kWh/day')

        self.assertEqual(energy, [{
            'name': 'P1_GKWh_20A_SOM',
            'period': 'P1',
            'price': 0.116,
            'units': 'kWh/day'}]
        )

    def test__get_GkWh_price_3X(self):
        tariff = Tariff(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, 'GKWh', 'kWh/day')

        self.assertEqual(energy, [
            {
                'name': 'P1_GKWh_30A_SOM',
                'period': 'P1',
                'price': 0.092,
                'units': 'kWh/day'
            },
            {
                'name': 'P2_GKWh_30A_SOM',
                'period': 'P2',
                'price': 0.081,
                'units': 'kWh/day'
            },
            {
                'name': 'P3_GKWh_30A_SOM',
                'period': 'P3',
                'price': 0.064,
                'units': 'kWh/day'
            }]
        )

    def test__get_tariff_historical_prices_2X(self):
        tariff = Tariff(self.tariff_id_2x)
        prices = tariff.priceDetail

        self.assertEqual(prices, self.json4test['tariff2X']['priceHistory'])


    def test__get_tariff_2X(self):
        tariff = Tariff(self.tariff_id_2x)
        tariff_json = tariff.tariff

        self.assertEqual(tariff_json, self.json4test['tariff2X'])


    def test__get_tariff_3X(self):
        tariff = Tariff(self.tariff_id_3x)
        tariff_json = tariff.tariff

        self.assertEqual(tariff_json, self.json4test['tariff3X'])
