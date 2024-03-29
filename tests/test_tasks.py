from unittest import TestCase

from erppeek import Client

from config import config
from infoenergia_api import tasks


class TestContracts(TestCase):
    def setUp(self):
        self.erp_client = Client(**config.ERP_CONF)

    def test__get_current_tariff(self):
        tariff_json = tasks.get_current_tariff(self.erp_client, 172830)
        self.assertDictEqual(
            tariff_json,
            {
                "tariffId": "2.1A",
                "dateStart": "2019-10-01T00:00:00+01:00",
                "dateEnd": "2021-05-31T00:00:00+01:00",
            },
        )

    def test__get_tariffHistory(self):
        tariff_json = tasks.get_tariffHistory(
            self.erp_client, [41931, 161180, 2656, 38396]
        )
        self.assertListEqual(
            tariff_json,
            [
                {
                    "tariffId": "2.0A",
                    "dateStart": "2012-11-28T00:00:00+01:00",
                    "dateEnd": "2019-05-31T00:00:00+01:00",
                },
                {
                    "tariffId": "2.0DHA",
                    "dateStart": "2019-06-01T00:00:00+01:00",
                    "dateEnd": "2021-05-31T00:00:00+01:00",
                },
            ],
        )

    def test__get_current_power(self):
        power_json = tasks.get_current_power(self.erp_client, 172830)
        self.assertDictEqual(
            power_json,
            {
                "power": 12500,
                "dateStart": "2019-10-01T00:00:00+01:00",
                "dateEnd": "2021-05-31T00:00:00+01:00",
            },
        )

    def test__get_powerHistory(self):
        power_json = tasks.get_powerHistory(self.erp_client, [2, 27737, 169970, 23586])
        self.assertListEqual(
            power_json,
            [
                {
                    "power": 6600,
                    "dateStart": "2011-11-22T00:00:00+01:00",
                    "dateEnd": "2019-09-01T00:00:00+01:00",
                },
                {
                    "power": 3400,
                    "dateStart": "2019-09-02T00:00:00+01:00",
                    "dateEnd": "2021-05-31T00:00:00+01:00",
                },
            ],
        )

    def test__get_devices(self):
        devices_json = tasks.get_devices(self.erp_client, [165130])
        self.assertListEqual(
            devices_json,
            [
                {
                    "dateStart": "2019-10-03T00:00:00+01:00",
                    "dateEnd": None,
                    "deviceId": "5fe0a4b4-8e6c-56d8-a74e-97f979411a62",
                }
            ],
        )

    def test__get_contract_address(self):
        address_json = tasks.get_contract_address(self.erp_client, 8)
        self.assertDictEqual(
            address_json,
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
        address_json = tasks.get_building_details(self.erp_client, [3])
        self.assertDictEqual(
            address_json,
            {
                "buildingConstructionYear": 2000,
                "dwellingArea": 100,
                "propertyType": False,
                "buildingType": "Single_house",
                "dwellingPositionInBuilding": False,
                "dwellingOrientation": False,
                "buildingWindowsType": False,
                "buildingWindowsFrame": "wood",
                "buildingCoolingSource": False,
                "buildingHeatingSource": "other",
                "buildingHeatingSourceDhw": "electricity",
                "buildingSolarSystem": False,
            },
        )

    def test__get_building_no_building_id(self):
        building_json = tasks.get_building_details(self.erp_client, None)
        self.assertEqual(building_json, None)

    def test__get_eprofile(self):
        profile_json = tasks.get_eprofile(self.erp_client, 3)
        self.assertDictEqual(
            profile_json,
            {
                "totalPersonsNumber": 3,
                "minorsPersonsNumber": 1,
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

    def test__get_no_eprofile(self):
        profile_json = tasks.get_eprofile(self.erp_client, None)
        self.assertEqual(profile_json, None)

    def test__get_no_service(self):
        service_json = tasks.get_service(self.erp_client, None)
        self.assertEqual(service_json, {})

    def test_get_version(self):
        version = tasks.get_version(self.erp_client, 159406)
        self.assertEqual(version, 6)

    def test_get_report(self):
        report_json = tasks.get_report(self.erp_client, "2011-11-22", 2104)
        self.assertDictEqual(
            report_json,
            {
                "language": "ca_ES",
                "initialMonth": 201111,
            },
        )

    def test_get_experimentalgroup(self):
        experimental_group = tasks.get_experimentalgroup(self.erp_client, 4)
        self.assertEqual(experimental_group, True)

    def test_climaticZone_from_cups(self):
        climaticZone = tasks.get_cups_to_climaticZone(self.erp_client, 4)
        self.assertEqual(climaticZone, "C2")
