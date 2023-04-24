from pony.orm import db_session

from datetime import datetime, timedelta, date

from infoenergia_api.contrib import TariffPrice

from tests.base import BaseTestCase


class TestBaseTariff(BaseTestCase):

    @db_session
    def test__get_tariff_2A(self):

        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {
            "type": "2.0A",
            "from_": "2021-03-01",
            "to_": "2021-05-31"
        }
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/tariff",
                params=params,
                headers={"Authorization": "Bearer {}".format(token)},
                timeout=None,
            )
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "data": self.json4test["price2A"]["data_TwoPrices"],
                "total_results": 1
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_tariff__2TD_with_tariff_name(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {
            "type": "2.0TD",
        }

        _, response = self.loop.run_until_complete(
            self.client.get(
                "/tariff",
                headers={"Authorization": "Bearer {}".format(token)},
                params=params,
                timeout=None,
            )
        )

        self.assertEqual(response.status, 200)
        prices = response.json['data'][0]['prices']
        self.assertTrue(
            len(prices) > 0
        )
        self.delete_user(user)

    @db_session
    def test__get_tariff__20TD_with_tariff_id(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )

        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {
            "tariffPriceId": 43,
            "withTaxes": False,
        }
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/tariff",
                headers={"Authorization": "Bearer {}".format(token)},
                params=params,
                timeout=None,
            )
        )
        self.assertEqual(response.status, 200)

        prices = response.json['data'][0]['prices']
        taxes = response.json['data'][0]['prices']['current']['taxes']
        tariffPriceId = response.json['data'][0]['tariffPriceId']
        self.assertTrue(
            len(prices) > 0
        )
        self.assertTrue(
            tariffPriceId == 43
        )
        self.assertEqual(taxes, {})
        self.delete_user(user)

    @db_session
    def test__get_tariff__3A_with_prices(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {
            "type": "3.0A",
            "from_": "2021-03-01",
            "to_": "2021-05-31",
        }
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/tariff",
                headers={"Authorization": "Bearer {}".format(token)},
                params=params,
                timeout=None,
            )
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json, {
                "count": 1,
                "data": self.json4test["price3A"]["data_prices"],
                'total_results': 1
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_tariff__20TD_without_user(self):
        params = {
            "tariffPriceId": 43,
        }
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/tariff",
                params=params,
                timeout=None,
            )
        )
        self.assertEqual(response.status, 200)

        prices = response.json['data'][0]['prices']
        tariffPriceId = response.json['data'][0]['tariffPriceId']
        self.assertTrue(
            len(prices) > 0
        )
        self.assertTrue(
            tariffPriceId == 43
        )


class TestTariff(BaseTestCase):

    tariff_id_2TD = 43
    tariff_id_3TD = 44
    tariff_id_6TD = 45

    filters = {'municipi_id': 3830}

    def test__create_tariff(self):
        tariff = TariffPrice(self.filters, self.tariff_id_2TD)

        self.assertIsInstance(tariff, TariffPrice)

    def test__tariff_prices__active_20TD_OK(self):
       # Get today's tariff
        tariff = TariffPrice( self.filters, self.tariff_id_2TD)
        _prices = tariff.tariff

        self.assertTrue(_prices['prices']['current']['dateStart'])
        self.assertEqual(_prices['tariffPriceId'], self.tariff_id_2TD)
        self.assertEqual(0, len(_prices['prices']['history']))

    def test__get_erp_tariff_prices__date_range_20TD_OK(self):
        self.filters['from_'] = '2021-01-01'
        self.filters['to_'] = date.today().strftime("%Y-%m-%d")

        tariff = TariffPrice( self.filters, self.tariff_id_2TD)
        _prices = tariff.tariff

        # For a large date range we should get more than one tariff version
        self.assertGreater(len(_prices['prices']['history']), 0)
        # Check if tariff's version start date starts one day after end date of previous version
        self.assertEqual(
            datetime.strptime(_prices['prices']['current']['dateStart'], "%Y-%m-%d"),
            datetime.strptime(_prices['prices']['history'][0]['dateEnd'], "%Y-%m-%d")+ timedelta(days=1)
        )

    def test__get_erp_tariff_prices__active_30TD_OK(self):
       # Get today's tariff
       tariff = TariffPrice(self.filters, self.tariff_id_3TD)
       _prices = tariff.tariff

       self.assertTrue(_prices['prices']['current']['dateStart'])
       self.assertEqual(0, len(_prices['prices']['history']))

    def test__get_erp_tariff_prices__not_found(self):
        self.filters['from_'] = '2020-01-01'
        self.filters['to_'] = '2021-01-01'
        tariff = TariffPrice(self.filters, self.tariff_id_2TD)
        _prices = tariff.tariff

        self.assertEqual(_prices, None)

    def test__get_erp_tariff_prices__2TD_price_power(self):
        # Select old prices for tariff 2.0TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'
        tariff = TariffPrice(self.filters, self.tariff_id_2TD)
        prices = tariff.tariff

        self.assertEqual(prices['prices']['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['prices']['history'][0]['power'],
           {
               'P1': {'unit': '€/kW/dia', 'value': 0.076668},
               'P2': {'unit': '€/kW/dia', 'value': 0.008118},
           }
        )
    def test__get_erp_tariff_prices__2TD_price_energy(self):
         # Select old prices for tariff 2.0TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'
        tariff = TariffPrice( self.filters, self.tariff_id_2TD)
        prices = tariff.tariff
        self.assertEqual(prices['prices']['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['prices']['history'][0]['activeEnergy'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.343},
               'P2': {'unit': '€/kWh', 'value': 0.281},
               'P3': {'unit': '€/kWh', 'value': 0.234},
           }
        )

    def test__get_erp_tariff_prices__2TD_price_gkwh(self):
        # Select old prices for tariff 2.0TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'
        tariff = TariffPrice(self.filters, self.tariff_id_2TD)
        prices = tariff.tariff
        self.assertEqual(prices['prices']['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['prices']['history'][0]['gkwh'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.170},
               'P2': {'unit': '€/kWh', 'value': 0.120},
               'P3': {'unit': '€/kWh', 'value': 0.095},
           }
        )
    def test__get_erp_tariff_prices__3TD_price_gkwh(self):
        # Select old prices for tariff 3.0TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'
        tariff = TariffPrice( self.filters, self.tariff_id_3TD)
        prices = tariff.tariff

        self.assertEqual(
            prices['prices']['history'][0]['gkwh'],
            {
                'P1': {'unit': '€/kWh', 'value': 0.144},
                'P2': {'unit': '€/kWh', 'value': 0.132},
                'P3': {'unit': '€/kWh', 'value': 0.104},
                'P4': {'unit': '€/kWh', 'value': 0.093},
                'P5': {'unit': '€/kWh', 'value': 0.082},
                'P6': {'unit': '€/kWh', 'value': 0.089}
            }
        )

    def test__get_erp_tariff_prices__2TD_price_autoconsumo(self):
        # Select old prices for tariff 2.0TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'

        tariff = TariffPrice(self.filters, self.tariff_id_2TD)
        prices = tariff.tariff

        self.assertEqual(prices['prices']['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['prices']['history'][0]['autoconsumo'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.176},
               'P2': {'unit': '€/kWh', 'value': 0.176},
               'P3': {'unit': '€/kWh', 'value': 0.176},
           }
        )

    def test__get_erp_tariff_prices__6TD_price_reactive(self):
        # Select old prices for tariff 6.1TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'
        tariff = TariffPrice(self.filters, self.tariff_id_6TD)
        prices = tariff.tariff

        self.assertEqual(
            prices['prices']['history'][0]['reactiveEnergy'],
            {
                'BOE núm. 76 - 30/03/2022': {
                    '0 - 0.80': {
                        'unit': '€/kVArh',
                        'value': 0.062332
                    },
                    '0.80 - 0.95': {
                        'unit': '€/kVArh',
                        'value': 0.041554
                    }
                }
            }
        )

    def test__get_erp_tariff_prices__2TD_price_energy_with_taxes(self):
         # Select old prices for tariff 2.0TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'
        self.filters['withTaxes'] = True

        tariff = TariffPrice( self.filters, self.tariff_id_2TD)
        prices = tariff.tariff
        self.assertEqual(prices['prices']['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['prices']['history'][0]['activeEnergy'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.417105},
               'P2': {'unit': '€/kWh', 'value': 0.34171},
               'P3': {'unit': '€/kWh', 'value': 0.284556},
           }
        )

    def test__get_erp_tariff_prices__2TD_price_energy_with_taxes_canarias(self):
         # Select old prices for tariff 2.0TD
        self.filters['from_'] = '2022-10-01'
        self.filters['to_'] = '2022-12-01'
        self.filters['withTaxes'] = True
        self.filters['geographicalRegion'] = "canarias"

        tariff = TariffPrice(self.filters, self.tariff_id_2TD)
        prices = tariff.tariff

        self.assertEqual(prices['prices']['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['prices']['history'][0]['activeEnergy'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.344715},
               'P2': {'unit': '€/kWh', 'value': 0.282405},
               'P3': {'unit': '€/kWh', 'value': 0.23517},
           }
        )
        self.assertEqual(len(prices['prices']['history'][0]['taxes']), 3)
