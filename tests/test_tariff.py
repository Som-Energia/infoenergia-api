from pony.orm import db_session

from datetime import datetime, timedelta, date

from infoenergia_api.contrib import TariffPrice

from tests.base import BaseTestCase


class TestBaseTariff(BaseTestCase):
    @db_session
    async def test__get_tariff_2A(self):
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
            "tariff": "2.0A",
        }
        _, response = await self.client.get(
            "/tariff",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {"count": 6, "data": self.json4test["price2A"]["data_AllPriceId"]},
        )
        self.delete_user(user)

    @db_session
    async def test__get_tariff__2A_with_priceId(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {"tariff": "2.0A", "tariffPriceId": 4}
        _, response = await self.client.get(
            "/tariff",
            headers={"Authorization": "Bearer {}".format(token)},
            params=params,
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {"count": 1, "data": self.json4test["price2A"]["data_OnePriceId"]},
        )
        self.delete_user(user)

    @db_session
    async def test__get_tariff__20TD(self):
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
            "tariff": "2.0TD",
        }
        _, response = await self.client.get(
            "/tariff",
            headers={"Authorization": "Bearer {}".format(token)},
            params=params,
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 5,
                "data": self.json4test["price20TD"]["data_MoreThanOnePriceId"],
            },
        )
        self.delete_user(user)

    @db_session
    async def test__get_tariff__3A(self):
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
            "tariff": "3.0A",
        }
        _, response = await self.client.get(
            "/tariff",
            headers={"Authorization": "Bearer {}".format(token)},
            params=params,
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json, {"count": 11, "data": self.json4test["price3A"]["data"]}
        )
        self.delete_user(user)

    @db_session
    async def test__get_tariff__by_contract_id(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        _, response = await self.client.get(
            "/tariff/0000004",
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {"count": 1, "data": self.json4test["price20TD"]["data_OnePriceId"]},
        )
        self.delete_user(user)


class TestTariff(BaseTestCase):

    tariff_id_2TD = 43
    tariff_id_3TD = 44
    tariff_id_6TD = 45

    filters = {'municipi_id': 3830}

    def test__create_tariff(self):
        tariff = TariffPrice(self.tariff_id_2TD, self.filters)

        self.assertIsInstance(tariff, TariffPrice)

    def test__get_erp_tariff_prices__active_20TD_OK(self):
       # Get today's tariff
       tariff = TariffPrice(self.tariff_id_2TD, self.filters)
       _prices = tariff.get_erp_tariff_prices
       self.assertFalse(_prices['current']['dateEnd'])

       self.assertEqual(0, len(_prices['history']))

    def test__get_erp_tariff_prices__date_range_20TD_OK(self):
        self.filters['date_from'] = '2021-01-01'
        self.filters['date_to'] = date.today().strftime("%Y-%m-%d")

        tariff = TariffPrice(self.tariff_id_2TD, self.filters)
        _prices = tariff.get_erp_tariff_prices

        # For a large date range we should get more than one tariff version
        self.assertGreater(len(_prices['history']), 0)
        # Check if tariff's version start date starts one day after end date of previous version
        self.assertEqual(
            datetime.strptime(_prices['current']['dateStart'], "%Y-%m-%d"),
            datetime.strptime(_prices['history'][0]['dateEnd'], "%Y-%m-%d")+ timedelta(days=1)
        )

    def test__get_erp_tariff_prices__active_30TD_OK(self):
       # Get today's tariff
       tariff = TariffPrice(self.tariff_id_3TD, self.filters)
       _prices = tariff.get_erp_tariff_prices
       self.assertFalse(_prices['current']['dateEnd'])

       self.assertEqual(0, len(_prices['history']))

    def test__get_erp_tariff_prices__not_found(self):
        self.filters['date_from'] = '2020-01-01'
        self.filters['date_to'] = '2021-01-01'
        tariff = TariffPrice(self.tariff_id_2TD, self.filters)
        _prices = tariff.get_erp_tariff_prices

        self.assertEqual(_prices, {'error': 'Tariff pricelist not found'})

    def test__get_erp_tariff_prices__2TD_price_power(self):
        # Select old prices for tariff 2.0TD
        self.filters['date_from'] = '2022-10-01'
        self.filters['date_to'] = '2022-12-01'
        tariff = TariffPrice(self.tariff_id_2TD, self.filters)
        prices = tariff.get_erp_tariff_prices
        self.assertEqual(prices['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['history'][0]['power'],
           {
               'P1': {'unit': '€/kW/dia', 'value': 0.076668},
               'P2': {'unit': '€/kW/dia', 'value': 0.008118},
           }
        )
    def test__get_erp_tariff_prices__2TD_price_energy(self):
         # Select old prices for tariff 2.0TD
        self.filters['date_from'] = '2022-10-01'
        self.filters['date_to'] = '2022-12-01'
        tariff = TariffPrice(self.tariff_id_2TD, self.filters)
        prices = tariff.get_erp_tariff_prices
        self.assertEqual(prices['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['history'][0]['activeEnergy'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.343},
               'P2': {'unit': '€/kWh', 'value': 0.281},
               'P3': {'unit': '€/kWh', 'value': 0.234},
           }
        )

    def test__get_erp_tariff_prices__2TD_price_gkwh(self):
        # Select old prices for tariff 2.0TD
        self.filters['date_from'] = '2022-10-01'
        self.filters['date_to'] = '2022-12-01'
        tariff = TariffPrice(self.tariff_id_2TD, self.filters)
        prices = tariff.get_erp_tariff_prices
        self.assertEqual(prices['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['history'][0]['GKWh'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.170},
               'P2': {'unit': '€/kWh', 'value': 0.120},
               'P3': {'unit': '€/kWh', 'value': 0.095},
           }
        )
    def test__get_erp_tariff_prices__3TD_price_gkwh(self):
        # Select old prices for tariff 3.0TD
        self.filters['date_from'] = '2022-10-01'
        self.filters['date_to'] = '2022-12-01'
        tariff = TariffPrice(self.tariff_id_3TD, self.filters)
        prices = tariff.get_erp_tariff_prices
        self.assertEqual(
            prices['history'][0]['GKWh'],
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
        self.filters['date_from'] = '2022-10-01'
        self.filters['date_to'] = '2022-12-01'

        tariff = TariffPrice(self.tariff_id_2TD, self.filters)
        prices = tariff.get_erp_tariff_prices

        self.assertEqual(prices['history'][0]['dateEnd'], '2022-12-31')
        self.assertEqual(
           prices['history'][0]['autoconsumo'],
           {
               'P1': {'unit': '€/kWh', 'value': 0.176},
               'P2': {'unit': '€/kWh', 'value': 0.176},
               'P3': {'unit': '€/kWh', 'value': 0.176},
           }
        )

    def test__get_GkWh_price3X(self):
        tariff = TariffPrice(self.tariff_id_3x)
        energy = tariff.termPrice(self.items_id_2019_3X, "GKWh", "€/kWh")

        self.assertEqual(
            energy,
            [
                {"period": "P1", "price": 0.092, "units": "€/kWh"},
                {"period": "P2", "price": 0.081, "units": "€/kWh"},
            ],
        )

    def test__get_tariff_historical_prices_2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        prices = tariff.priceDetail
        self.assertEqual(
            prices, self.json4test["price2A"]["data_OnePriceId"][0]["price"]
        )

    def test__get_reactive_energy(self):
        reactive_energy = ReactiveEnergyPrice.create().reactiveEnergy
        self.assertEqual(reactive_energy, self.json4test["reactiveEnergy"])

    def test__get_tariff_2X(self):
        tariff = TariffPrice(self.tariff_id_2x)
        tariff_json = tariff.tariff
        self.assertEqual(tariff_json, self.json4test["price2A"]["data_OnePriceId"][0])
