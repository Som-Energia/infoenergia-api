import functools
from datetime import datetime

from sanic.log import logger

from infoenergia_api.contrib.climatic_zones import ine_to_zc
from infoenergia_api.contrib.postal_codes import ine_to_dp

from ..tasks import find_changes
from ..utils import (get_id_for_contract, get_request_filters,
                     make_utc_timestamp, make_uuid)


def get_contract_json(erp_client, contract):
    profile_obj = erp_client.model('empowering.modcontractual.profile')
    building_obj = erp_client.model('empowering.cups.building')
    service_obj = erp_client.model('empowering.modcontractual.service')

    modi_contract = contract['modcontractuals_ids']
    profile_id = get_id_for_contract(
        profile_obj,
        modi_contract
    )
    service_id = get_id_for_contract(
        service_obj,
        modi_contract
    )
    building_id = building_obj.search(
        [
            ('cups_id', '=', contract['cups'][0])
        ]
    )
    contract_json = {
        'contractId': contract['name'],
        'ownerId': make_uuid('res.partner', contract['titular'][0]),
        'payerId': make_uuid('res.partner', contract['pagador'][0]),
        'dateStart': make_utc_timestamp(contract['data_alta']),
        'dateEnd': make_utc_timestamp(contract['data_baixa']),
        'tariffId': contract['tarifa'][1],
        'tariff_': get_current_tariff(
            erp_client,
            contract['modcontractual_activa'][0]
        ),
        'tariffHistory': get_tariffHistory(
            erp_client,
            contract['modcontractuals_ids']
        ),
        'power': int(contract['potencia'] * 1000),
        'power_': get_current_power(
            erp_client,
            contract['modcontractual_activa'][0]
        ),
        'powerHistory': get_powerHistory(
            erp_client,
            contract['modcontractuals_ids'],
        ),
        'terciaryPower': get_tertiaryPower(
            erp_client,
            contract['tarifa'][1],
            contract['id']
        ),
        'climaticZone': get_cups_to_climaticZone(
            erp_client,
            contract['cups'][0]
        ),
        'activityCode': contract['cnae'][1],
        'customer': {
            'customerId': make_uuid(
                'res.partner',
                contract['titular'][0]
            ),
            'address': get_contract_address(
                erp_client,
                contract['cups'][0]
            ),
            'meteringPointId': make_uuid(
                'giscedata.cups.ps',
                contract['cups'][1]
            ),
            'buildingData': get_building_details(
                erp_client,
                building_id
            ),
            'profile': get_eprofile(
                erp_client,
                profile_id
            ),
            'customisedServiceParameters': get_service(
                erp_client,
                service_id
            )
        },
        'devices': get_devices(
            erp_client,
            contract['comptadors']
        ),
        'report': get_report(
            erp_client,
            contract['data_alta'],
            contract['pagador'][0]
        ),
        'version': get_version(
            erp_client,
            contract['modcontractual_activa'][0]
        ),
        'experimentalGroupUserTest': False,
        'experimentalGroupUser': get_experimentalgroup(
            erp_client,
            contract['cups'][0]
        ),
    }
    return contract_json


def get_contracts(request, id_contract=None):
    contract_obj = request.app.erp_client.model('giscedata.polissa')

    FIELDS = [
        'id',
        'name',
        'titular',
        'data_alta',
        'data_baixa',
        'potencia',
        'tarifa',
        'pagador',
        'modcontractual_activa',
        'comptadors',
        'cups',
        'soci',
        'cnae',
        'modcontractuals_ids',
        'autoconsumo',
        'persona_fisica',
        'titular_nif'
    ]

    def __init__(self, contract_id):
        from infoenergia_api.app import app

        self._erp = app.erp_client
        self._Polissa= self._erp.model('giscedata.polissa')
        for name, value in self._Polissa.read(contract_id, self.FIELDS).items():
            setattr(self, name, value)

    @property
    def currentTariff(self):
        """
        Current tariff:
        "tariff_": {
          "tariffId": "tariffID-123",
          "dateStart": "2014-10-11T00:00:00Z",
          "dateEnd": null,
        }
        """
        modcon = find_changes(self._erp, self.modcontractual_activa[0], 'tarifa')[-1]

        return {
            "tariffId": modcon['tarifa'][1],
            "dateStart": make_utc_timestamp(modcon['data_inici']),
            "dateEnd": make_utc_timestamp(modcon['data_final'])
        }

    @property
    def tariffHistory(self):
        """
        "tariffHistory": [
         {
          "tariffId": "tariffID-123",
          "dateStart": "2014-10-11T00:00:00Z",
          "dateEnd": null,
         },
         {
           "tariffId": "tariffID-122",
           "dateStart": "2013-10-11T16:37:05Z",
           "dateEnd": "2014-10-10T23:59:59Z"
          }
        ]
        """
        return [
            {
                "tariffId": modcon['tarifa'][1],
                "dateStart": make_utc_timestamp(modcon['data_inici']),
                "dateEnd": make_utc_timestamp(modcon['data_final'])
            }
            for modcon in find_changes(self._erp, self.modcontractuals_ids, 'tarifa')]

    @property
    def currentPower(self):
        """
        Current power:
        "power_": {
          "power": 123,
          "dateStart": "2014-10-11T00:00:00Z",
          "dateEnd": null,
        }
        """
        modcon = find_changes(self._erp, self.modcontractual_activa[0], 'potencia')[-1]
        return {
            "power": int(modcon['potencia'] * 1000),
            "dateStart": make_utc_timestamp(modcon['data_inici']),
            "dateEnd": make_utc_timestamp(modcon['data_final'])
        }

    @property
    def powerHistory(self):
        """
        powerHistory:
        "powerHistory": [
          {
            "power": 122,
            "dateStart": "2013-10-11T16:37:05Z",
            "dateEnd": "2014-10-10T23:59:59Z"
          }
        ]
        """
        return [
            {
                "power": int(modcon['potencia'] * 1000),
                "dateStart": make_utc_timestamp(modcon['data_inici']),
                "dateEnd": make_utc_timestamp(modcon['data_final'])
            }
            for modcon in find_changes(self._erp, self.modcontractuals_ids, 'potencia')]

    @property
    def tertiaryPower(self):
        """
        Terciary Power:
         {
            "P1": 20000,
            "P2": 20000,
            "P3": 20000
        }
        """
        if '2.' in self.tarifa:
            return {}
        period_obj = self._erp.model('giscedata.polissa.potencia.contractada.periode')
        period_powers = period_obj.read([('polissa_id', '=', self.id)])
        return {
         'P{}'.format(i): int(period['potencia'] * 1000) for i, period in enumerate(period_powers, 1)
        }

    @property
    def climaticZone(self):
        """
        Climatic zone from CTE DB-HE:
        """
        if not self.cups[0]:
            return None
        cups_obj = self._erp.model('giscedata.cups.ps')
        muni_obj = self._erp.model('res.municipi')

        cups = cups_obj.read(self.cups[0], ['id_municipi'])
        ine = muni_obj.read(cups['id_municipi'][0], ['ine'])['ine']
        if ine in ine_to_zc.keys():
            return ine_to_zc[ine]
        else:
            return None

    @property
    def address(self):
        """
        Adress details:
        {
            'city': 'Barcelona',
            'cityCode': '08019',
            'countryCode': 'ES',
            'postalCode': '8016',
            'provinceCode': '08',
            'province': 'Barcelona',
        }
        """
        cups_obj = self._erp.model('giscedata.cups.ps')
        muni_obj = self._erp.model('res.municipi')
        state_obj = self._erp.model('res.country.state')
        sips_obj = self._erp.model('giscedata.sips.ps')

        cups_fields = ['id_municipi', 'tv', 'nv', 'cpa', 'cpo', 'pnp', 'pt',
                       'name', 'es', 'pu', 'dp']
        cups = cups_obj.read(self.cups[0], cups_fields)
        muni_id = cups['id_municipi'][0]
        postal_code = cups['dp']

        ine = muni_obj.read(muni_id, ['ine'])['ine']
        state_id = muni_obj.read(muni_id, ['state'])['state'][0]
        state = state_obj.read(state_id, ['code', 'name'])
        sips_id = sips_obj.search([('name', '=', cups['name'])])
        #if not postal_code:  to do fix postal code in DDBB
        if sips_id:
            postal_code = sips_obj.read(
                int(sips_id[0]),
                ['codi_postal']
            )['codi_postal']
        else:
            if ine in ine_to_dp:
                postal_code = ine_to_dp[ine]
        address = {
            'city': cups['id_municipi'][1],
            'cityCode': ine,
            'countryCode': 'ES',
            'postalCode': postal_code,
            'provinceCode': state['code'],
            'province': state['name']
        }
        return address

    @property
    def buildingDetails(self):
        """
        Building details
         {
              "buildingConstructionYear": 2014,
              "dwellingArea": 196,
              "propertyType": "primary",
              "buildingType": "Apartment",
              "dwellingPositionInBuilding": "first_floor",
              "dwellingOrientation": "SE",
              "buildingWindowsType": "double_panel",
              "buildingWindowsFrame": "PVC",
              "buildingCoolingSource": "electricity",
              "buildingHeatingSource": "district_heating",
              "buildingHeatingSourceDhw": "gasoil",
              "buildingSolarSystem": "not_installed"
         }
        """
        building_obj = self._erp.model('empowering.cups.building')

        building_id = building_obj.search([('cups_id', '=', self.cups[0])])
        if not building_id:
            return None

        fields = [
            'buildingConstructionYear',
            'dwellingArea',
            'propertyType',
            'buildingType',
            'dwellingPositionInBuilding',
            'dwellingOrientation',
            'buildingWindowsType',
            'buildingWindowsFrame',
            'buildingCoolingSource',
            'buildingHeatingSource',
            'buildingHeatingSourceDhw',
            'buildingSolarSystem'
        ]
        building = building_obj.read(building_id, fields)[0]
        return {field: building[field] for field in fields}

    @property
    def eprofile(self):
        """ Profile
        {
          "totalPersonsNumber": 3,
          "minorsPersonsNumber": 0,
          "workingAgePersonsNumber": 2,
          "retiredAgePersonsNumber": 1,
          "malePersonsNumber": 2,
          "femalePersonsNumber": 1,
          "educationLevel":
            {
                "edu_prim": 0,
                "edu_sec": 1,
                "edu_uni": 1,
                "edu_noStudies": 1
            }
        }
        """
        profile_obj = self._erp.model('empowering.modcontractual.profile')
        profile_id = get_id_for_contract(profile_obj, self.modcontractuals_ids)

        if not profile_id:
            return None

        fields = [
            'totalPersonsNumber',
            'minorPersonsNumber',
            'workingAgePersonsNumber',
            'retiredAgePersonsNumber',
            'malePersonsNumber',
            'femalePersonsNumber',
            'eduLevel_prim',
            'eduLevel_sec',
            'eduLevel_uni',
            'eduLevel_noStudies'
        ]

        profile = profile_obj.read(profile_id, fields)
        return {
            'totalPersonsNumber': profile['totalPersonsNumber'],
            'minorsPersonsNumber': profile['minorPersonsNumber'],
            'workingAgePersonsNumber': profile['workingAgePersonsNumber'],
            'retiredAgePersonsNumber': profile['retiredAgePersonsNumber'],
            'malePersonsNumber': profile['malePersonsNumber'],
            'femalePersonsNumber': profile['femalePersonsNumber'],
            'educationLevel': {
                'edu_prim': profile['eduLevel_prim'],
                'edu_sec': profile['eduLevel_sec'],
                'edu_uni': profile['eduLevel_uni'],
                'edu_noStudies': profile['eduLevel_noStudies']
            }
        }

    @property
    def service(self):
        """
        Convert service
         {
            "OT701": "p1;P2;px"
         }
        """
        service_obj = self._erp.model('empowering.modcontractual.service')
        service_id = get_id_for_contract(service_obj, self.modcontractuals_ids)

        if not service_id:
            return {}

        fields = [
            'OT101',
            'OT103',
            'OT105',
            'OT106',
            'OT109',
            'OT201',
            'OT204',
            'OT401',
            'OT502',
            'OT503',
            'OT603',
            'OT603g',
            'OT701',
            'OT703'
        ]
        service = service_obj.read(service_id, fields)
        return {field: service[field] for field in fields}

    @property
    def devices(self):
        """
        All devices:
        [
          {
            'dateStart': '2019-10-03T00:00:00-00:15Z',
            'dateEnd': None,
            'deviceId': 'ee3f4996-788e-59b3-9530-0e02d99b45b7'
          }
        ]
        """
        if not self.comptadors:
            return []

        compt_obj = self._erp.model('giscedata.lectures.comptador')
        fields = ['data_alta', 'data_baixa']

        devices = []
        for comptador in compt_obj.read(self.comptadors, fields) or []:
            devices.append(
                {
                    'dateStart': make_utc_timestamp(comptador['data_alta']),
                    'dateEnd': make_utc_timestamp(comptador['data_baixa']),
                    'deviceId': make_uuid(
                        'giscedata.lectures.comptador',
                        comptador['id']
                    )
                }
            )
        return devices

    @property
    def report(self):
        """
        Report.
        {
            "language": "ca_ES",
            "initialMonth": "201701"
        }
        """
        partner_obj = self._erp.model('res.partner')
        partner = partner_obj.read(self.titular[0], ['lang'])

        initial_month = datetime.strptime(self.data_alta, '%Y-%m-%d').strftime('%Y%m')
        return {
            'language': partner['lang'],
            'initialMonth': int(initial_month),
        }

    @property
    def version(self):
        """
        Get active contract modification's name
        int
        """
        modcontract_obj = self._erp.model('giscedata.polissa.modcontractual')
        version = modcontract_obj.read( self.modcontractual_activa[0], ['name'])
        return int(version['name'])

    @property
    def experimentalGroup(self):
        """
        If a contract has empowering return True, False otherwise
        """
        cups_obj = self._erp.model('giscedata.cups.ps')
        return cups_obj.read(self.cups[0], ['empowering'])['empowering'] or False

    @property
    def selfConsumption(self):
        """
        If a contract has self-consumption return True, False otherwise
        """
        if self.autoconsumo == '00':
            return False
        else:
            return True


    @property
    def juridicType(self):
        """
        Contract owner juridic type:
        'juridicPerson-ESJ' (where ESJ are the first 3 letters of CIF)
        or
        physicalPerson
        """
        if self.persona_fisica == 'CI':
            return str.join('-', ('juridicPerson', self.titular_nif[:3]))
        else:
            return 'physicalPerson'

    @property
    def contracts(self):
        return {
            'contractId': self.name,
            'ownerId': make_uuid('res.partner', self.titular[0]),
            'payerId': make_uuid('res.partner', self.pagador[0]),
            'dateStart': make_utc_timestamp(self.data_alta),
            'dateEnd': make_utc_timestamp(self.data_baixa),
            'autoconsumo': self.selfConsumption,
            'juridicType': self.juridicType,
            'tariffId': self.tarifa[1],
            'tariff_': self.currentTariff,
            'tariffHistory': self.tariffHistory,
            'power': int(self.potencia * 1000),
            'power_': self.currentPower,
            'powerHistory': self.powerHistory,
            'terciaryPower': self.tertiaryPower,
            'climaticZone': self.climaticZone,
            'activityCode': self.cnae[1],
            'customer': {
                'customerId': make_uuid('res.partner', self.titular[0]),
                'address': self.address,
                'meteringPointId': make_uuid('giscedata.cups.ps', self.cups[1]),
                'buildingData': self.buildingDetails,
                'profile': self.eprofile,
                'customisedServiceParameters': self.service
            },
            'devices': self.devices,
            'report': self.report,
            'version': self.version,
            'experimentalGroupUserTest': False,
            'experimentalGroupUser': self.experimentalGroup
        }



    if request.args:
        filters = get_request_filters(
            request.app.erp_client,
            request,
            filters,
        )
    logger.debug('Filter contracts by: %s', filters)
    if id_contract:
        return contract_obj.read(
            contract_obj.search([('name', '=', id_contract)]), fields
        )[0] or {}
    id_contracts = contract_obj.search(filters)
    return contract_obj.read(id_contracts, fields) or []


async def async_get_contracts(request, id_contract=None):
    try:
        result = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_contracts, request, id_contract)
        )
    except Exception as e:
        raise e
    return result


async def async_get_contract_json(loop, executor, erp_client, sem, contract):
    async with sem:
        result = await loop.run_in_executor(
            executor,
            functools.partial(get_contract_json, erp_client, contract)
        )
    return result
