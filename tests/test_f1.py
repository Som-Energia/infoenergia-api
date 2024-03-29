from unittest import mock, skip

from pony.orm import db_session

from infoenergia_api.contrib import Invoice

from tests.base import BaseTestCase


class TestF1(BaseTestCase):
    @mock.patch("infoenergia_api.contrib.f1.get_invoices")
    @db_session
    async def test__get_f1_measures_by_contract_id(self, get_invoices_mock):
        get_invoices_mock.return_value = [8174595]
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)

        request, response = await self.client.get(
            "/f1/{}".format(self.json4test["invoices_f1_by_contract_id"]["contractId"]),
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "total_results": 1,
                "data": [
                    self.json4test["invoices_f1_by_contract_id"]["contract_data"][0]
                ],
            },
        )
        self.delete_user(user)

    @mock.patch("infoenergia_api.contrib.f1.get_invoices")
    @db_session
    async def test__get_f1_measures(self, async_get_invoices_mock):
        async_get_invoices_mock.return_value = [7568406]
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
            "from_": "2019-09-01",
            "to_": "2019-09-01",
            "tariff": "3.1A",
            "limit": 1,
        }

        request, response = await self.client.get(
            "/f1",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "total_results": 1,
                "data": self.json4test["invoices_f1"]["contract_data"],
            },
        )
        self.delete_user(user)

    @mock.patch("infoenergia_api.contrib.f1.get_invoices")
    @mock.patch("infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor")
    @db_session
    async def test__get_f1_measure_pagination(
        self, next_cursor_mock, get_invoices_mock
    ):
        get_invoices_mock.return_value = [7590942, 7730323, 8174595]
        next_cursor_mock.return_value = (
            "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0="
        )
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
            "from_": "2019-09-01",
            "to_": "2019-09-01",
            "tariff": "3.1A",
            "limit": 1,
        }

        request, response = await self.client.get(
            "/f1",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "total_results": 3,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/f1?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc
                ),
                "data": [self.json4test["f1pagination"]["contract_data"][0]],
            },
        )
        self.delete_user(user)

    @mock.patch("infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor")
    @db_session
    async def test__get_f1_measure_pagination__20TD(self, next_cursor_mock):
        next_cursor_mock.return_value = (
            "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0="
        )
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {"tariff": "2.0TD", "limit": 1}

        request, response = await self.client.get(
            "/f1",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "total_results": 3610,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/f1?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc
                ),
                "data": [self.json4test["f1pagination"]["contract_data_20TD"][0]],
            },
        )
        self.delete_user(user)

    @mock.patch("infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor")
    @db_session
    async def test__get_f1_measure_pagination__30TD(self, next_cursor_mock):
        next_cursor_mock.return_value = (
            "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0="
        )
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {"tariff": "3.0TD", "limit": 1}

        request, response = await self.client.get(
            "/f1",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "total_results": 9,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/f1?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc
                ),
                "data": [self.json4test["f1pagination"]["contract_data_30TD"][0]],
            },
        )
        self.delete_user(user)

    @skip("review pagination process in PaginationLinksMixin")
    @mock.patch("infoenergia_api.contrib.f1.get_invoices")
    @mock.patch("infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor")
    @db_session
    async def test__get_f1_measure_pagination_with_cursor(
        self, next_cursor_mock, get_invoices_mock
    ):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        request, response = await self.client.get(
            "http://127.0.0.1:54167/f1?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1",
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "total_results": 1,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/f1?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc
                ),
                "data": [self.json4test["f1pagination"]["contract_data"][0]],
            },
        )
        self.delete_user(user)

    @db_session
    async def test__get_f1_measures_without_permission(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=False,
            category="Energética",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)

        request, response = await self.client.get(
            "/f1/{}?limit=1".format(
                self.json4test["invoices_f1_by_contract_id"]["contractId"]
            ),
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 0,
                "total_results": 0,
                "data": [],
            },
        )
        self.delete_user(user)


class TestInvoice(BaseTestCase):

    invoice_id_2x = 17615667
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
                    "dateStart": "2022-06-28T00:00:00+02:00",
                    "dateEnd": None,
                    "deviceId": "4385c40f-388c-50ff-94b8-ccb9d3607ec6",
                }
            ],
        )

    def test__f1_power_2X(self):
        a_20td_invoice_id_without_f1_values = 202528
        invoice = Invoice(a_20td_invoice_id_without_f1_values)

        f1_power = invoice.f1_power_kW

        self.assertListEqual(f1_power, [])

    def test__f1_power_3X(self):
        invoice = Invoice(self.invoice_id_3x)

        f1_power = invoice.f1_power_kW
        self.assertListEqual(
            f1_power,
            [
                {"excess": 0.0, "maximeter": 29.0, "period": "P1", "units": "kW"},
                {"excess": 0.0, "maximeter": 12.0, "period": "P2", "units": "kW"},
                {"excess": 0.0, "maximeter": 3.0, "period": "P3", "units": "kW"},
                {"excess": 0.0, "maximeter": 25.0, "period": "P4", "units": "kW"},
                {"excess": 0.0, "maximeter": 26.0, "period": "P5", "units": "kW"},
                {"excess": 0.0, "maximeter": 15.0, "period": "P6", "units": "kW"},
            ],
        )

    def test__get_f1_reactive_energy_2X(self):
        invoice = Invoice(self.invoice_id_2x)

        f1_reactive_energy = invoice.f1_reactive_energy_kVArh
        self.assertListEqual(f1_reactive_energy, [])

    def test__get_f1_reactive_energy_3X(self):
        invoice = Invoice(self.invoice_id_3x)

        f1_reactive_energy = invoice.f1_reactive_energy_kVArh
        self.assertListEqual(
            f1_reactive_energy,
            [
                {"consum": 41, "period": "P1", "source": "TPL", "units": "kVArh"},
                {"consum": 13, "period": "P2", "source": "TPL", "units": "kVArh"},
                {"consum": 0, "period": "P3", "source": "TPL", "units": "kVArh"},
                {"consum": 11, "period": "P4", "source": "TPL", "units": "kVArh"},
                {"consum": 24, "period": "P5", "source": "TPL", "units": "kVArh"},
                {"consum": 46, "period": "P6", "source": "TPL", "units": "kVArh"},
            ],
        )

    def test__get_f1_active_energy_2X(self):
        invoice = Invoice(self.json4test["invoice_20TD"]["id"])

        f1_active_energy = invoice.f1_active_energy_kWh

        self.assertListEqual(
            f1_active_energy, self.json4test["invoice_20TD"]["f1_active_energy"]
        )

    def test__get_f1_active_energy_3X(self):
        invoice = Invoice(self.invoice_id_3x)

        f1_active_energy = invoice.f1_active_energy_kWh

        self.assertListEqual(
            f1_active_energy,
            [
                {
                    "consum": 307,
                    "period": "P1",
                    "source": "TPL",
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "consum": 324,
                    "period": "P2",
                    "source": "TPL",
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "consum": 113,
                    "period": "P3",
                    "source": "TPL",
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "consum": 94,
                    "period": "P4",
                    "source": "TPL",
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "consum": 209,
                    "period": "P5",
                    "source": "TPL",
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "consum": 212,
                    "period": "P6",
                    "source": "TPL",
                    "magnitud": "AE",
                    "units": "kWh",
                },
            ],
        )

    def test__get_f1_active_energy_3X_auto(self):
        invoice = Invoice(15674108)

        f1_reactive_energy = invoice.f1_active_energy_kWh

        self.assertListEqual(
            f1_reactive_energy,
            [
                {
                    "source": "Estimada",
                    "period": "P1",
                    "consum": 0,
                    "magnitud": "AS",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P1",
                    "consum": 0,
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P2",
                    "consum": 0,
                    "magnitud": "AS",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P2",
                    "consum": 0,
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P3",
                    "consum": 22,
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P3",
                    "consum": 0,
                    "magnitud": "AS",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P4",
                    "consum": 0,
                    "magnitud": "AS",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P4",
                    "consum": 17,
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P5",
                    "consum": 0,
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P5",
                    "consum": 0,
                    "magnitud": "AS",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P6",
                    "consum": 228,
                    "magnitud": "AE",
                    "units": "kWh",
                },
                {
                    "source": "Estimada",
                    "period": "P6",
                    "consum": 0,
                    "magnitud": "AS",
                    "units": "kWh",
                },
            ],
        )

    def test_f1_measures_2x(self):
        invoice = Invoice(self.invoice_id_2x)

        f1_measures = invoice.f1_measures

        self.assertDictEqual(
            f1_measures,
            self.json4test["invoices_f1_by_contract_id"]["contract_data"][0],
        )

    def test__f1_maximeter(self):
        invoice = Invoice(13281874)

        f1_maximeter = invoice.f1_maximeter
        self.assertListEqual(
            f1_maximeter,
            [
                {
                    "dateStart": "2021-06-01",
                    "dateEnd": "2021-09-09",
                    "maxPower": 4.352,
                    "period": "2.0TD (P1)",
                },
                {
                    "dateStart": "2021-06-01",
                    "dateEnd": "2021-09-09",
                    "maxPower": 2.5,
                    "period": "2.0TD (P2)",
                },
            ],
        )

    def test__f1_maximeter__without_results(self):
        a_20td_invoice_id_without_maximeter_values = 283681
        invoice = Invoice(a_20td_invoice_id_without_maximeter_values)

        f1_maximeter = invoice.f1_maximeter

        self.assertListEqual(f1_maximeter, [])
