from pony.orm import db_session
from unittest import mock
from datetime import datetime, timedelta, date

from tests.base import BaseTestCase

from infoenergia_api.contrib import Contract


class TestBaseContracts(BaseTestCase):
    patch_next_cursor = (
        "infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor"
    )

    @db_session
    def test__get_contracts_by_id__2A(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/contracts/" + self.json4test["contract_id_2A"]["contractId"],
                headers={"Authorization": "Bearer {}".format(token)},
                timeout=None,
            )
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "data": [self.json4test["contract_id_2A"]["contract_data"]],
                "total_results": 1,
            },
        )
        self.delete_user(user)

    @mock.patch(patch_next_cursor)
    @db_session
    def test__get_contracts__20TD(self, next_cursor_mock):
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
            "from_": "2015-10-03",
            "to_": "2015-10-03",
            "tariff": "2.0TD",
            "juridic_type": "physical_person",
            "limit": 1,
        }

        _, response = self.loop.run_until_complete(
            self.client.get(
                "/contracts",
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
                "data": self.json4test["contract_20TD"],
                "total_results": 9,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/contracts?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc.decode("utf-8")
                ),
            },
        )
        self.delete_user(user)

    @db_session
    def test__get_contracts__30TD(self):
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
            "from_": "2012-07-12",
            "to_": "2012-07-14",
            "tariff": "3.0TD",
            "limit": 1,
        }

        _, response = self.loop.run_until_complete(
            self.client.get(
                "/contracts",
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
                "data": self.json4test["contract_30TD"],
                "total_results": 1,
            },
        )
        self.delete_user(user)

    @db_session
    def test__get_contracts__3X(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)

        _, response = self.loop.run_until_complete(
            self.client.get(
                "/contracts/" + self.json4test["contract_id_3X"]["contractId"],
                headers={"Authorization": "Bearer {}".format(token)},
                timeout=None,
            )
        )
        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "data": self.json4test["contract_id_3X"]["contract_data"],
                "total_results": 1,
            },
        )
        self.delete_user(user)

    @db_session
    def test__get_contracts_without_permission(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=False,
            category="Energética",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/contracts/" + self.json4test["contract_id_2A"]["contractId"],
                headers={"Authorization": "Bearer {}".format(token)},
                timeout=None,
            )
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json, {"count": 0, "data": [], "total_results": 0}
        )
        self.delete_user(user)

    @db_session
    def test__get_contract_energetica(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=False,
            category="Energética",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/contracts/" + self.json4test["contract_energetica"]["contractId"],
                headers={"Authorization": "Bearer {}".format(token)},
                timeout=None,
            )
        )
        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "data": self.json4test["contract_energetica"]["contract_data"],
                "total_results": 1,
            },
        )
        self.delete_user(user)

    @db_session
    def test__get_contract_tariff_by_id__2TD(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        token = self.get_auth_token(user.username, self.dummy_passwd)
        _, response = self.loop.run_until_complete(
            self.client.get(
                "/contracts/0000004/tariff",
                headers={"Authorization": "Bearer {}".format(token)},
                timeout=None,
            )
        )

        self.assertEqual(response.status, 200)

        response_data = response.json["data"][0]
        current = response_data["current"]["prices"]
        history_prices = []
        for prices in response_data["history"]:
            history_prices.extend(prices["prices"])
        history = sorted(history_prices, key= lambda x: x["dateStart"], reverse=True)
        # Check if tariff"s version start date starts one day after end date of previous
        self.assertEqual(
            datetime.strptime(current["dateStart"], "%Y-%m-%d"),
            datetime.strptime(history[0]["dateEnd"], "%Y-%m-%d")+ timedelta(days=1)
        )

        self.delete_user(user)


class TestContracts(BaseTestCase):

    contract_id = 49794
    contract_id_3X = 158697

    def test__create_contract(self):
        contract = Contract(self.contract_id)
        self.assertIsInstance(contract, Contract)

    def test__get_current_tariff(self):
        contract = Contract(self.contract_id)
        tariff = contract.currentTariff
        self.assertDictEqual(
            tariff,
            {
                "tariffId": "2.0TD",
                "tariffPriceId": 101,
                "dateStart": "2022-01-11T00:00:00+01:00",
                "dateEnd": "2024-03-09T00:00:00+01:00"
            }
        )

    def test__get_tariffHistory(self):
        contract = Contract(13)
        tariff_history = contract.tariffHistory
        self.assertListEqual(
            tariff_history,
            [
                {
                    "tariffId": "2.0A",
                    "tariffPriceId": 4,
                    "dateStart": "2011-12-31T00:00:00+01:00",
                    "dateEnd": "2019-06-05T00:00:00+02:00"
                },
                {
                    "tariffId": "2.0DHS",
                    "tariffPriceId": 18,
                    "dateStart": "2019-06-06T00:00:00+02:00",
                    "dateEnd": "2021-05-31T00:00:00+02:00"
                },
                {
                "tariffId": "2.0TD",
                "tariffPriceId": 101,
                "dateStart": "2021-06-01T00:00:00+02:00",
                "dateEnd": "2024-04-17T00:00:00+02:00"
                }
            ]
        )

    def test__get_current_power(self):
        contract = Contract(self.contract_id)
        power = contract.currentPower
        self.assertDictEqual(
            power,
            {
                "power": {"P1-2": 4500, "P3": 4500},
                "dateStart": "2022-01-11T00:00:00+01:00",
                "dateEnd": "2024-03-09T00:00:00+01:00",
                "measurement_point": "05"
            }
        )

    def test__get_powerHistory(self):
        contract = Contract(self.contract_id)
        power = contract.powerHistory
        self.assertListEqual(
            power,
            [
                {
                    "power": {"P1": 4400.0},
                    "dateStart": "2015-03-10T00:00:00+01:00",
                    "dateEnd": "2017-08-30T00:00:00+02:00",
                    "measurement_point": "05"
                },
                {
                    "power": {"P1": 3450.0},
                    "dateStart": "2017-08-31T00:00:00+02:00",
                    "dateEnd": "2021-05-31T00:00:00+02:00",
                    "measurement_point": "05"
                },
                {
                    "power": {"P1-2": 3450.0, "P3": 3450.0},
                    "dateStart": "2021-06-01T00:00:00+02:00",
                    "dateEnd": "2021-11-25T00:00:00+01:00",
                    "measurement_point": "05"
                },
                {
                    "power": {"P1-2": 4500.0, "P3": 4500.0},
                    "dateStart": "2021-11-26T00:00:00+01:00",
                    "dateEnd": "2024-03-09T00:00:00+01:00",
                    "measurement_point": "05"
                }
            ]
        )

    def test__get_climaticZone_from_cups(self):
        contract = Contract(self.contract_id)
        climaticZone = contract.climaticZone
        self.assertEqual(climaticZone, "C2")

    def test__get_contract_address(self):
        contract = Contract(self.contract_id)
        address = contract.address
        self.assertDictEqual(
            address,
            {
                "city": "Caldes de Malavella",
                "cityCode": "17033",
                "countryCode": "ES",
                "postalCode": "17456",
                "provinceCode": "17",
                "province": "Girona"
            }
        )

    def test__get_building_details(self):
        contract = Contract(self.contract_id)
        building = contract.buildingDetails
        self.assertDictEqual(
            building,
            {
                "buildingConstructionYear": 1985,
                "buildingCoolingSource": "other",
                "buildingHeatingSource": "gas",
                "buildingHeatingSourceDhw": "gas",
                "buildingSolarSystem": "not_installed",
                "buildingType": "Single_house",
                "buildingWindowsFrame": "wood",
                "buildingWindowsType": "double_panel",
                "dwellingArea": 100,
                "dwellingOrientation": "S",
                "dwellingPositionInBuilding": "first_floor",
                "propertyType": "primary"
            },
        )

    def test__get_eprofile(self):
        contract = Contract(self.contract_id)
        profile = contract.eprofile
        self.assertDictEqual(
            profile,
            {
                "totalPersonsNumber": 3,
                "minorsPersonsNumber": 1,
                "workingAgePersonsNumber": 2,
                "retiredAgePersonsNumber": False,
                "malePersonsNumber": False,
                "femalePersonsNumber": False,
                "educationLevel": {
                    "edu_prim": False,
                    "edu_sec": False,
                    "edu_uni": False,
                    "edu_noStudies": False
                }
            }
        )

    def test__get_no_service(self):
        contract = Contract(self.contract_id)
        service = contract.service
        self.assertEqual(service, {})

    def test__get_report(self):
        contract = Contract(self.contract_id)
        report = contract.report
        self.assertDictEqual(
            report,
            {
                "language": "ca_ES",
                "initialMonth": 201503,
            },
        )

    def test__get_version(self):
        contract = Contract(self.contract_id)
        version = contract.version
        self.assertEqual(version, 5)

    def test__get_experimentalgroup(self):
        contract = Contract(self.contract_id)
        experimental_group = contract.experimentalGroup
        self.assertEqual(experimental_group, True)

    def test__get_selfConsumptionType(self):
        contract = Contract(self.contract_id)
        self_consumption = contract.selfConsumption
        self.assertEqual(self_consumption, "[41] - Con excedentes y compensación Individual - Consumo")

    def test__get_selfConsumptionInstalledPower(self):
        contract = Contract(self.contract_id)
        self.assertEqual(contract.installedPower, 4.45)

    def test__get_juridicType_physical_person(self):
        contract = Contract(self.contract_id)
        physical_person = contract.juridicType
        self.assertEqual(physical_person, "physicalPerson")

    def test__get_juridicType_juridic_person(self):
        contract = Contract(self.contract_id_3X)
        juridic_person = contract.juridicType
        self.assertEqual(juridic_person, "juridicPerson-ESH")

    def test__get_devices(self):
        contract = Contract(self.contract_id)
        devices = contract.devices
        self.assertListEqual(
            devices,
            [
                {
                    "dateStart": "2020-10-23T00:00:00+02:00",
                    "dateEnd": None,
                    "deviceId": "35edccba-f211-5f05-8932-73fb305664d3"
                },
                {
                    "dateStart": "2017-07-28T00:00:00+02:00",
                    "dateEnd": "2020-10-23T00:00:00+02:00",
                    "deviceId": "2eba5491-173b-5f2d-a36c-1a5f16f5ca17"
                },
                {
                    "dateStart": "2015-03-10T00:00:00+01:00",
                    "dateEnd": "2017-07-27T00:00:00+02:00",
                    "deviceId": "59092b2b-49e3-5d9d-8440-66d8f9748d23"
                }
            ]
        )
