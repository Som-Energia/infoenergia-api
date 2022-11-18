from unittest import mock

from pony.orm import db_session

from tests.base import BaseTestCase


class TestModContracts(BaseTestCase):
    patch_next_cursor = (
        "infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor"
    )

    @mock.patch(patch_next_cursor)
    @db_session
    def test__get_modcontracts__canceled(self, next_cursor_mock):
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
            "from_": "2019-09-17",
            "to_": "2019-09-17",
            "type": "canceled",
            "limit": 1,
        }
        _, response = self.client.get(
            "/modcontracts",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "total_results": 34,
                "count": 1,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/modcontracts?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc
                ),
                "data": self.json4test["contracts_canceled"]["contract_data"],
            },
        )
        self.delete_user(user)

    @mock.patch(patch_next_cursor)
    @db_session
    def test__get_modcontracts__tariffOrPower(self, next_cursor_mock):
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
            "from_": "2021-06-02",
            "to_": "2021-06-02",
            "type": "tariff_power",
            "limit": 1,
        }
        _, response = self.client.get(
            "/modcontracts",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "total_results": 59,
                "count": 1,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/modcontracts?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc
                ),
                "data": self.json4test["contracts_mod_tariff_power"]["contract_data"],
            },
        )
        self.delete_user(user)

    @db_session
    def test__get_modcontracts__without_permission(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=False,
            category="Energética",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        params = {
            "from_": "2019-10-19",
            "to_": "2019-10-19",
            "type": "tariff_power",
        }
        _, response = self.client.get(
            "/modcontracts",
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json, {"total_results": 0, "count": 0, "data": []}
        )
        self.delete_user(user)

    @db_session
    def test__get_modcontracts__by_contract(self):
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
            "from_": "2000-10-01",
            "to_": "2021-10-19",
            "type": "tariff_power",
        }
        _, response = self.client.get(
            "/modcontracts/" + self.json4test["modcontract_by_id"]["contractId"],
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            timeout=None,
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "total_results": 1,
                "count": 1,
                "data": self.json4test["modcontract_by_id"]["contract_data"],
            },
        )
        self.delete_user(user)
