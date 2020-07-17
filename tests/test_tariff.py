from unittest import mock, skip

from pony.orm import db_session

from infoenergia_api.contrib import Tariff

from tests.base import BaseTestCase

class TestTariff(BaseTestCase):

    tariff_id_2x = 4
    tariff_id_3x = 12
    items_id_2X = [331, 332, 333, 589]
    items_id_3X =[860, 861, 862, 863, 864, 865, 866, 867, 868]


    def test__create_tariff(self):
        tariff = Tariff(self.tariff_id_2x)

        self.assertIsInstance(tariff, Tariff)

    def test__get_active_energy_price2X(self):
        tariff = Tariff(self.tariff_id_2x)
        energy = tariff.term(self.items_id_2X, 'energia', 'kWh/day')

        self.assertEqual(energy, [{
            'name': 'P1_ENERGIA_20ASOM',
            'period': 'P1',
            'price': 0.144833,
            'units': 'kWh/day'}]
        )

    def test__get_active_energy_price3X(self):
        tariff = Tariff(self.tariff_id_3x)
        energy = tariff.term(self.items_id_3X, 'energia', 'kWh/day')

        self.assertEqual(energy, [
            {
                'name': 'P1_ENERGIA_3.0A',
                'period': 'P1',
                'price': 0.174501,
                'units': 'kWh/day'
            },
            {
                'name': 'P2_ENERGIA_3.0A',
                'period': 'P2',
                'price': 0.129482,
                'units': 'kWh/day'
            },
            {
                'name': 'P3_ENERGIA_3.0A',
                'period': 'P3',
                'price': 0.075032,
                'units': 'kWh/day'
            },
            ]
        )

    def test__get_reactive_energy_price3X(self):
        tariff = Tariff(self.tariff_id_3x)
        energy = tariff.term(self.items_id_3X, 'reactiva', 'kWh/day')

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
        energy = tariff.term(self.items_id_2X, 'reactiva', 'kWh/day')

        self.assertEqual(energy, [{
            'name': 'P1_REACTIVA_20ASOM',
            'period': 'P1',
            'price': 0.0,
            'units': 'kWh/day'}]
        )

    def test__get_power_price2X(self):
        tariff = Tariff(self.tariff_id_2x)
        energy = tariff.term(self.items_id_2X, 'potencia', 'kW/year')

        self.assertEqual(energy, [{
            'name': 'P1_POTENCIA_20ASOM',
            'period': 'P1',
            'price': 18.633129,
            'units': 'kW/year'}]
        )

    def test__get_pwer_price3X(self):
        tariff = Tariff(self.tariff_id_3x)
        energy = tariff.term(self.items_id_3X, 'potencia', 'kW/year')

        self.assertEqual(energy, [
            {
                'name': 'P1_POTENCIA_3.0A',
                'period': 'P1',
                'price': 15.754249,
                'units': 'kW/year'
            },
            {
                'name': 'P2_POTENCIA_3.0A',
                'period': 'P2',
                'price': 9.452549,
                'units': 'kW/year'
            },
            {
                'name': 'P3_POTENCIA_3.0A',
                'period': 'P3',
                'price': 6.3017,
                'units': 'kW/year'
            },
            ]
        )

    # def test_get_GkWh_price2X(self):
    #     tariff = Tariff(self.tariff_id_2x)
    #     energy = tariff.term(self.items_id_2X, 'GKWh', 'kWh/day')
    #
    #     self.assertEqual(energy, [{
    #         'name': 'P1_GKWh_20A_SOM',
    #         'period': 'P1',
    #         'price': 0.116,
    #         'units': 'kWh/day'}]
    #     )
