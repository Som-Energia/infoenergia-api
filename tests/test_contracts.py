from passlib.hash import pbkdf2_sha256
from pony.orm import db_session

from tests.base import BaseTestCase

from infoenergia_api.contrib import Contract


class TestBaseContracts(BaseTestCase):

    @db_session
    def test__get_contracts_by_id__2A(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        _, response = self.client.get(
            '/contracts/' + self.json4test['contract_id_2A']['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 1,
                'data': [self.json4test['contract_id_2A']['contract_data']],
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_contracts__20DHS(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2019-10-03',
            'to_': '2019-10-09',
            'tariff': '2.0DHS',
            'juridic_type': 'physical_person',
        }
        _, response = self.client.get(
            '/contracts',
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 2,
                'data': self.json4test['contracts_20DHS']['contract_data'],
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_contracts__3X(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")

        _, response = self.client.get(
            '/contracts/' + self.json4test['contract_id_3X']['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 1,
                'data': self.json4test['contract_id_3X']['contract_data'],

            }
        )
        self.delete_user(user)


    @db_session
    def test__get_contracts_without_permission(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=False,
            category='Energética'
        )
        token = self.get_auth_token(user.username, "123412345")
        _, response = self.client.get(
            '/contracts/' + self.json4test['contract_id_2A']['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 0,
                'data': [],
            }
        )
        self.delete_user(user)

    @db_session
    def test__get_contract_energetica(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=False,
            category='Energética'
        )
        token = self.get_auth_token(user.username, "123412345")
        _, response = self.client.get(
            '/contracts/' + self.json4test['contract_energetica']['contractId'],
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 1,
                'data': self.json4test['contract_energetica']['contract_data'],
            }
        )
        self.delete_user(user)

class TestContracts(BaseTestCase):

    contract_id = 4
    contract_id_3X = 158697

    def test__create_invoice(self):
        contract = Contract(self.contract_id)

        self.assertIsInstance(contract, Contract)

    def test__get_current_tariff(self):
        contract = Contract(self.contract_id)
        tariff = contract.currentTariff
        self.assertDictEqual(
            tariff,
            {
              'dateEnd': '2020-11-21T00:00:00-00:15Z',
              'dateStart': '2019-09-02T00:00:00-00:15Z',
              'tariffId': '2.0A'
            }
        )

    def test__get_tariffHistory(self):
        contract = Contract(self.contract_id)
        tariff_history = contract.tariffHistory
        self.assertListEqual(
            tariff_history,
            [
                {
                    'dateEnd': '2020-11-21T00:00:00-00:15Z',
                    'dateStart': '2011-11-22T00:00:00-00:15Z',
                    'tariffId': '2.0A'
                }
            ]
        )

    def test__get_current_power(self):
        contract = Contract(self.contract_id)
        power = contract.currentPower
        self.assertDictEqual(
            power,
            {
                'power': 3400,
                'dateStart': '2019-09-02T00:00:00-00:15Z',
                'dateEnd': '2020-11-21T00:00:00-00:15Z'
            }
        )

    def test__get_powerHistory(self):
        contract = Contract(self.contract_id)
        power = contract.powerHistory
        self.assertListEqual(
            power,
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
        contract = Contract(self.contract_id_3X)
        tertiary_power = contract.tertiaryPower
        self.assertEqual(
            tertiary_power,
            {
                'P1': 4000,
                'P2': 4000,
                'P3': 15001
            }
        )

    def test__get_climaticZone_from_cups(self):
        contract = Contract(self.contract_id)
        climaticZone = contract.climaticZone
        self.assertEqual(
            climaticZone,
            'C2'
        )

    def test__get_contract_address(self):
        contract = Contract(self.contract_id)
        address =contract.address
        self.assertDictEqual(
            address,
            {
                'city': 'Barcelona',
                'cityCode': '08019',
                'countryCode': 'ES',
                'postalCode': '08036',
                'provinceCode': '08',
                'province': 'Barcelona',
            }
        )

    def test__get_building_details(self):
        contract = Contract(self.contract_id)
        building = contract.buildingDetails
        self.assertDictEqual(
            building,
            {
                'buildingConstructionYear': 1999,
                'dwellingArea': 89,
                'propertyType': False,
                'buildingType': 'Apartment',
                'dwellingPositionInBuilding': False,
                'dwellingOrientation': False,
                'buildingWindowsType': False,
                'buildingWindowsFrame': '',
                'buildingCoolingSource': False,
                'buildingHeatingSource': 'other',
                'buildingHeatingSourceDhw': False,
                'buildingSolarSystem': False
            }
        )

    def test__get_eprofile(self):
        contract = Contract(self.contract_id)
        profile = contract.eprofile
        self.assertDictEqual(
            profile,
            {
                'totalPersonsNumber': 3,
                'minorsPersonsNumber': 0,
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

    def test__get_no_service(self):
        contract = Contract(self.contract_id)
        service = contract.service
        self.assertEqual(
            service,
            {}
        )

    def test__get_report(self):
        contract = Contract(self.contract_id)
        report = contract.report
        self.assertDictEqual(
            report,
            {
                'language': 'ca_ES',
                'initialMonth': 201111,
            }
        )

    def test__get_version(self):
        contract = Contract(self.contract_id)
        version = contract.version
        self.assertEqual(
            version,
            4
        )

    def test__get_experimentalgroup(self):
        contract = Contract(self.contract_id)
        experimental_group = contract.experimentalGroup
        self.assertEqual(
            experimental_group,
            True
        )

    def test__get_selfConsumption(self):
        contract = Contract(self.contract_id)
        self_consumption = contract.selfConsumption
        self.assertEqual(
            self_consumption,
            False
        )

    def test__get_juridicType_physical_person(self):
        contract = Contract(self.contract_id)
        physical_person = contract.juridicType
        self.assertEqual(
            physical_person,
            'physicalPerson'
        )

    def test__get_juridicType_juridic_person(self):
        contract = Contract(self.contract_id_3X)
        juridic_person = contract.juridicType
        self.assertEqual(
            juridic_person,
            'juridicPerson-ESH'
        )
