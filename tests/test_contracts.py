from pony.orm import db_session
from unittest import mock

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
                "total_results": 12,
                "cursor": "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=",
                "next_page": "http://{}/contracts?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                    response.url.netloc
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
        self.assertDictEqual(
            response.json,
            {
                "count": 1,
                "data": [self.json4test["contract_id_2A"]["contract_data"]],
                "total_results": 1,
            },
        )
        self.delete_user(user)



class TestContracts(BaseTestCase):

    contract_id = 322497
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
                "dateEnd": "2021-11-21T00:00:00+01:00",
                "dateStart": "2021-06-01T00:00:00+01:00",
                "tariffId": "2.0TD",
                "tariffPriceId": 101,
            },
        )

    def test__get_tariffHistory(self):
        contract = Contract(13)
        tariff_history = contract.tariffHistory
        self.assertListEqual(
            tariff_history,
            [
                {
                    "dateEnd": "2019-06-05T00:00:00+01:00",
                    "dateStart": "2011-12-31T00:00:00+01:00",
                    "tariffId": "2.0A",
                    "tariffPriceId": 4,
                },
                {
                    "dateEnd": "2021-05-31T00:00:00+01:00",
                    "dateStart": "2019-06-06T00:00:00+01:00",
                    "tariffId": "2.0DHS",
                    "tariffPriceId": 18,
                },
                {
                    "dateEnd": "2021-12-30T00:00:00+01:00",
                    "dateStart": "2021-06-01T00:00:00+01:00",
                    "tariffId": "2.0TD",
                    "tariffPriceId": 101,
                },
            ],
        )

    def test__get_current_power(self):
        contract = Contract(self.contract_id)
        power = contract.currentPower
        self.assertDictEqual(
            power,
            {
                "power": {"P1-2": 3400, "P3": 3400},
                "dateStart": "2021-06-01T00:00:00+01:00",
                "dateEnd": "2021-11-21T00:00:00+01:00",
                "measurement_point": "05",
            },
        )

    def test__get_powerHistory(self):
        contract = Contract(self.contract_id)
        power = contract.powerHistory
        self.assertListEqual(
            power,
            [
                {
                    "power": {"P1": 6600.0},
                    "dateStart": "2011-11-22T00:00:00+01:00",
                    "dateEnd": "2019-09-01T00:00:00+01:00",
                    "measurement_point": "05",
                },
                {
                    "power": {"P1": 3400.0},
                    "dateStart": "2019-09-02T00:00:00+01:00",
                    "dateEnd": "2021-05-31T00:00:00+01:00",
                    "measurement_point": "05",
                },
                {
                    "power": {"P1-2": 3400.0, "P3": 3400.0},
                    "dateStart": "2021-06-01T00:00:00+01:00",
                    "dateEnd": "2021-11-21T00:00:00+01:00",
                    "measurement_point": "05",
                },
            ],
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
                "city": "Barcelona",
                "cityCode": "08019",
                "countryCode": "ES",
                "postalCode": "08036",
                "provinceCode": "08",
                "province": "Barcelona",
            },
        )

    def test__get_building_details(self):
        contract = Contract(self.contract_id)
        building = contract.buildingDetails
        self.assertDictEqual(
            building,
            {
                "buildingConstructionYear": 1999,
                "dwellingArea": 89,
                "propertyType": False,
                "buildingType": "Apartment",
                "dwellingPositionInBuilding": False,
                "dwellingOrientation": False,
                "buildingWindowsType": False,
                "buildingWindowsFrame": "",
                "buildingCoolingSource": False,
                "buildingHeatingSource": "other",
                "buildingHeatingSourceDhw": False,
                "buildingSolarSystem": False,
            },
        )

    def test__get_eprofile(self):
        contract = Contract(self.contract_id)
        profile = contract.eprofile
        self.assertDictEqual(
            profile,
            {
                "totalPersonsNumber": 3,
                "minorsPersonsNumber": 0,
                "workingAgePersonsNumber": False,
                "retiredAgePersonsNumber": False,
                "malePersonsNumber": False,
                "femalePersonsNumber": False,
                "educationLevel": {
                    "edu_prim": False,
                    "edu_sec": False,
                    "edu_uni": False,
                    "edu_noStudies": False,
                },
            },
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
                "initialMonth": 201111,
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

    def test__get_selfConsumption(self):
        contract = Contract(self.contract_id)
        self_consumption = contract.selfConsumption
        self.assertEqual(self_consumption, "[00] - Sin Autoconsumo")

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
                    "dateStart": "2011-12-23T00:00:00+01:00",
                    "dateEnd": None,
                    "deviceId": "ab201f66-4da7-517b-be40-13b7e0de7429",
                }
            ],
        )
