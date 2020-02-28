import os
from unittest import TestCase, skip

from api import tasks
from config import config
from erppeek import Client
from sanic.log import logger

os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.devel')


class TestF1Measures(TestCase):

    def setUp(self):
        self.erp_client = Client(**config.ERP_CONF)

    def test__get_f1_power_3X(self):
        f1_power_json = tasks.get_f1_power(
            self.erp_client,
            [5195892, 5195890, 5195891, 5195894, 5195895, 5195893],
            units='kW/dia'
        )
        self.assertListEqual(
            f1_power_json,
            [
                {
                    'period': 'P1',
                    'excess': 0.0,
                    'maximeter': 0.0,
                    'units': 'kW/dia'
                },
                {
                    'period': 'P2',
                    'excess': 0.0,
                    'maximeter': 2.0,
                    'units': 'kW/dia'
                },
                {
                    'period': 'P3',
                    'excess': 0.0,
                    'maximeter': 3.0,
                    'units': 'kW/dia'
                },
                {
                    'period': 'P4',
                    'excess': 0.0,
                    'maximeter': 0.0,
                    'units': 'kW/dia'
                },
                {
                    'period': 'P5',
                    'excess': 0.0,
                    'maximeter': 3.0,
                    'units': 'kW/dia'
                },
                {
                    'period': 'P6',
                    'excess': 0.0,
                    'maximeter': 3.0,
                    'units': 'kW/dia'
                }
            ],
        )

    def test__get_f1_power_2X(self):
        f1_power_json = tasks.get_f1_power(
            self.erp_client,
            [],
            units='kW/dia'
        )
        self.assertListEqual(
            f1_power_json,
            [],
        )

    def test__get_f1_reactive_energy_3X(self):
        f1_reactive_energy_json = tasks.get_f1_energy_measurements(
            self.erp_client,
            [9991237, 9991236, 9991235, 9991234, 9991233, 9991232, 9991231, 9991229, 9991228, 9991227, 9991226, 9991225],
            'reactiva',
            units='kVArh'
        )
        self.assertListEqual(
            f1_reactive_energy_json,
            [
                {
                    'source': 'Telemesura',
                    'period': 'P1',
                    'consum': 0,
                    'units': 'kVArh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P2',
                    'consum': 583,
                    'units': 'kVArh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P3',
                    'consum': 1198,
                    'units': 'kVArh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P4',
                    'consum': 0,
                    'units': 'kVArh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P5',
                    'consum': 250,
                    'units': 'kVArh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P6',
                    'consum': 520,
                    'units': 'kVArh'
                }
            ]
        )

    def test__get_f1_active_energy_3X(self):
        f1_active_energy_json = tasks.get_f1_energy_measurements(
            self.erp_client,
            [9991237, 9991236, 9991235, 9991234, 9991233, 9991232, 9991231, 9991229, 9991228, 9991227, 9991226, 9991225],
            'activa',
            units='kWh'
        )
        self.assertListEqual(
            f1_active_energy_json,
            [
                {
                    'source': 'Telemesura',
                    'period': 'P1',
                    'consum': 0,
                    'units': 'kWh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P2',
                    'consum': 144,
                    'units': 'kWh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P3',
                    'consum': 327,
                    'units': 'kWh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P4',
                    'consum': 0,
                    'units': 'kWh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P5',
                    'consum': 75,
                    'units': 'kWh'
                },
                {
                    'source': 'Telemesura',
                    'period': 'P6',
                    'consum': 146,
                    'units': 'kWh'
                }
            ]

        )

    def test__get_f1_reactive_energy_2X(self):
        f1_reactive_energy_json = tasks.get_f1_energy_measurements(
            self.erp_client,
            [10149986],
            'reactiva',
            units='kVArh'
        )
        self.assertListEqual(
            f1_reactive_energy_json,
            []
        )

    def test__get_f1_active_energy_2X(self):
        f1_active_energy_json = tasks.get_f1_energy_measurements(
            self.erp_client,
            [10149986],
            'activa',
            units='kWh'
        )
        self.assertListEqual(
            f1_active_energy_json,
            [
                {
                    'source': 'Telegestió',
                    'period': 'P1',
                    'consum': 156,
                    'units': 'kWh'
                }
            ]
        )


@skip
class TestContracts(TestCase):

    def setUp(self):
        self.erp_client = Client(**config.ERP_CONF)

    def test__get_current_tariff(self):
        tariff_json = tasks.get_current_tariff(self.erp_client, 172830)
        self.assertDictEqual(
            tariff_json,
            {
                'tariffId': '2.1A',
                'dateStart': '2019-10-01T00:00:00-00:15Z',
                'dateEnd': '2020-09-30T00:00:00-00:15Z'
            }
        )

    def test__get_tariffHistory(self):
        tariff_json = tasks.get_tariffHistory(
            self.erp_client,
            [41931, 161180, 2656, 38396]
        )
        self.assertListEqual(
            tariff_json,
            [
                {
                    'tariffId': '2.0A',
                    'dateStart': '2012-11-28T00:00:00-00:15Z',
                    'dateEnd': '2019-05-31T00:00:00-00:15Z'
                },
                {
                    'tariffId': '2.0DHA',
                    'dateStart': '2019-06-01T00:00:00-00:15Z',
                    'dateEnd': '2020-10-31T00:00:00-00:15Z'
                }
            ]
        )

    def test__get_current_power(self):
        power_json = tasks.get_current_power(self.erp_client, 172830)
        self.assertDictEqual(
            power_json,
            {
                'power': 12500,
                'dateStart': '2019-10-01T00:00:00-00:15Z',
                'dateEnd': '2020-09-30T00:00:00-00:15Z'
            }
        )

    def test__get_powerHistory(self):
        power_json = tasks.get_powerHistory(
            self.erp_client,
            [2, 27737, 169970, 23586]
        )
        self.assertListEqual(
            power_json,
            [
                {
                    'power': 6600,
                    'dateStart': '2011-11-22T00:00:00-00:15Z',
                    'dateEnd': '2019-09-01T00:00:00-00:15Z'
                },
                {
                    'power': 3400,
                    'dateStart': '2019-09-02T00:00:00-00:15Z',
                    'dateEnd': '2020-11-21T00:00:00-00:15Z'
                },
            ]
        )

    def test__get_tertiaryPower(self):
        tertiary_power_json = tasks.get_tertiaryPower(
            self.erp_client,
            '3.0A',
            '0080474'
        )
        self.assertEqual(
            tertiary_power_json,
            {
                'P1': 4000,
                'P2': 4000,
                'P3': 15001
            }
        )

    def test__get_devices(self):
        devices_json = tasks.get_devices(self.erp_client, [165130])
        self.assertListEqual(
            devices_json,
            [
                {
                    'dateStart': '2019-10-03T00:00:00-00:15Z',
                    'dateEnd': None,
                    'deviceId': '5fe0a4b4-8e6c-56d8-a74e-97f979411a62'
                }
            ]
        )

    def test__get_contract_address(self):
        address_json = tasks.get_contract_address(self.erp_client, 8)
        self.assertDictEqual(
            address_json,
            {
                'city': 'Barcelona',
                'cityCode': '08019',
                'countryCode': 'ES',
                'postalCode': '08016',
                'provinceCode': '08',
                'province': 'Barcelona',
            }
        )

    def test__get_building_details(self):
        address_json = tasks.get_building_details(self.erp_client, [3])
        self.assertDictEqual(
            address_json,
            {
                'buildingConstructionYear': 2000,
                'dwellingArea': 100,
                'propertyType': False,
                'buildingType': 'Single_house',
                'dwellingPositionInBuilding': False,
                'dwellingOrientation': False,
                'buildingWindowsType': False,
                'buildingWindowsFrame': 'wood',
                'buildingCoolingSource': False,
                'buildingHeatingSource': 'other',
                'buildingHeatingSourceDhw': 'electricity',
                'buildingSolarSystem': False
            }
        )

    def test__get_building_no_building_id(self):
        building_json = tasks.get_building_details(self.erp_client, None)
        self.assertEqual(
            building_json,
            None
        )

    def test__get_eprofile(self):
        profile_json = tasks.get_eprofile(self.erp_client, 3)
        self.assertDictEqual(
            profile_json,
            {
                'totalPersonsNumber': 3,
                'minorsPersonsNumber': 1,
                'workingAgePersonsNumber': False,
                'retiredAgePersonsNumber': False,
                'malePersonsNumber': False,
                'femalePersonsNumber': False,
                'educationLevel': {
                    'edu_prim': False,
                    'edu_sec': False,
                    'edu_uni': False,
                    'edu_noStudies': False
                }
            }
        )

    def test__get_no_eprofile(self):
        profile_json = tasks.get_eprofile(self.erp_client, None)
        self.assertEqual(
            profile_json,
            None
        )

    def test__get_no_service(self):
        service_json = tasks.get_service(self.erp_client, None)
        self.assertEqual(
            service_json,
            {}
        )

    def test_get_version(self):
        version = tasks.get_version(self.erp_client, 159406)
        self.assertEqual(
            version,
            6
        )

    def test_get_report(self):
        report_json = tasks.get_report(self.erp_client, '2011-11-22', 2104)
        self.assertDictEqual(
            report_json,
            {
                'language': 'ca_ES',
                'initialMonth': 201111,
            }
        )

    def test_get_experimentalgroup(self):
        experimental_group = tasks.get_experimentalgroup(self.erp_client, 4)
        self.assertEqual(
            experimental_group,
            True
        )

    def test_climaticZone_from_cups(self):
        climaticZone = tasks.get_cups_to_climaticZone(self.erp_client, 4)
        self.assertEqual(
            climaticZone,
            'C2'
        )
