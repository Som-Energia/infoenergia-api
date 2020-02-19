import functools
import re
from datetime import datetime

from sanic.log import logger

from .climatic_zones import ine_to_zc
from .postal_codes import ine_to_dp
from .utils import (get_id_for_contract, get_request_filters,
                    make_utc_timestamp, make_uuid)


def get_f1_measures_json(erp_client, invoice):
    units = erp_client.model('product.uom')
    f1_measures_json = {
        'contractId': invoice['polissa_id'][1],
        'invoiceId': make_uuid(
            'giscedata.facturacio.factura',
            invoice['id']
        ),
        'dateStart': make_utc_timestamp(invoice['data_inici']),
        'dateEnd': make_utc_timestamp(invoice['data_final']),
        'meteringPointId': make_uuid(
            'giscedata.cups.ps',
            invoice['cups_id'][1]
        ),
        'devices': get_devices(
            erp_client,
            invoice['comptadors']
        ),
        'power_measurements': get_f1_power(
            erp_client,
            invoice['lectures_potencia_ids'],
            units.read([('id', '=', 10)])[0]['name']

        ),
        'reactive_energy_measurements': get_f1_energy_measurements(
            erp_client,
            invoice['lectures_energia_ids'],
            'reactiva',
            units.read([('id', '=', 4)])[0]['name']

        ),
        'active_energy_measurements': get_f1_energy_measurements(
            erp_client,
            invoice['lectures_energia_ids'],
            'activa',
            units.read([('id', '=', 3)])[0]['name']
        ),
    }
    return f1_measures_json


def get_invoices(request, contractId=None):
    factura_obj = request.app.erp_client.model('giscedata.facturacio.factura')
    filters = [
        ('polissa_state', '=', 'activa'),
        ('type', '=', 'in_invoice')
    ]
    if contractId:
        filters.append(('polissa_id', '=', contractId))
        return factura_obj.read(
            factura_obj.search(filters)
        ) or []

    if request.args:
        filters = get_request_filters(
            request.app.erp_client,
            request,
            filters,
        )
    logger.info('Filter invoices by: %s', filters)
    id_invoices = factura_obj.search(filters)
    return factura_obj.read(id_invoices) or []


def get_f1_power(erp_client, power_readings_ids, units):
    """
    Readings F1:
    "power_measurements": {
      "period": "P1",
      "excess": "0.0",
      "maximeter": "2",
      "units": "kW/dia"
    }
    """

    power_obj = erp_client.model('giscedata.facturacio.lectures.potencia')
    f1_power = power_obj.read([('id', 'in', power_readings_ids)])
    return [
        {
            'period': power['name'],
            'excess': power['exces'],
            'maximeter': power['pot_maximetre'],
            'units': units
        } for power in f1_power]


def get_f1_energy_measurements(erp_client, energy_readings_ids, energy_type, units):
    """
    Readings F1:
    "energy_measurements": {
      "energyType": activa/reactiva
      "source": telegestión/real
      "period": "P1",
      "consum": "2",
      "units": "kWh"
    }
    """
    measures_obj = erp_client.model('giscedata.facturacio.lectures.energia')
    measures = measures_obj.read([('id', 'in', energy_readings_ids)])
    return [
        {
            'source': 'Not informed' if isinstance(measure['origen_id'], bool) else measure['origen_id'][1],
            'period': re.split('[()]', measure['name'])[1],
            'consum': int(measure['consum']),
            'units': units
        } for measure in measures if measure['tipus'] == energy_type]


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
    logger.info(contract['name'])
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
            contract['modcontractuals_ids']),
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

    filters = [
        ("active", "=", True),
        ("state", "=", "activa")
    ]
    fields = [
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
        'modcontractuals_ids'
    ]
    if request.args:
        logger.info('request.args: %s', request.args)
        filters = get_request_filters(
            request.app.erp_client,
            request.args,
            filters
        )
    logger.info('Filter contracts by: %s', filters)
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


async def async_get_contract_json(loop, executor, erp_client, contract):
    result = await loop.run_in_executor(
        executor,
        functools.partial(get_contract_json, erp_client, contract)
    )
    return result


async def assync_get_invoices(request, id_contract=None):
    try:
        result = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_invoices, request, id_contract)
        )
    except Exception as e:
        raise e
    return result


async def async_get_f1_measures_json(loop, executor, erp_client, invoices):
    result = await loop.run_in_executor(
        executor,
        functools.partial(get_f1_measures_json, erp_client, invoices)
    )
    return result


def find_changes(erp_client, modcons_id, field):
    modcon_obj = erp_client.model('giscedata.polissa.modcontractual')
    fields = ['data_inici', 'data_final', 'potencia', 'tarifa']

    modcons = modcon_obj.read(modcons_id, fields)
    # to do: re-write if
    if type(modcons) is dict:
        modcons = [modcon_obj.read(modcons_id, fields)]
    modcons = sorted(
        modcons,
        key=lambda k: k['data_inici']
    )
    prev_ = modcons[0]
    modcons_ = []
    for next_ in modcons[1:]:
        if prev_[field] != next_[field]:
            modcons_.append(prev_)
            prev_ = next_
        else:
            prev_['data_final'] = next_['data_final']
    modcons_.append(prev_)
    return modcons_


def get_current_tariff(erp_client, modcons_id):
    """
    Current tariff:
    "tariff_": {
      "tariffId": "tariffID-123",
      "dateStart": "2014-10-11T00:00:00Z",
      "dateEnd": null,
    }
    """
    modcon = find_changes(erp_client, modcons_id, 'tarifa')[-1]

    return {
        "tariffId": modcon['tarifa'][1],
        "dateStart": make_utc_timestamp(modcon['data_inici']),
        "dateEnd": make_utc_timestamp(modcon['data_final'])
    }


def get_tariffHistory(erp_client, modcons_ids):
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
        for modcon in find_changes(erp_client, modcons_ids, 'tarifa')]


def get_current_power(erp_client, modcons_id):
    """
    Current power:
    "power_": {
      "power": 123,
      "dateStart": "2014-10-11T00:00:00Z",
      "dateEnd": null,
    }
    """
    modcon = find_changes(erp_client, modcons_id, 'potencia')[-1]
    return {
        "power": int(modcon['potencia'] * 1000),
        "dateStart": make_utc_timestamp(modcon['data_inici']),
        "dateEnd": make_utc_timestamp(modcon['data_final'])
    }


def get_powerHistory(erp_client, modcons_id):
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
        for modcon in find_changes(erp_client, modcons_id, 'potencia')]


def get_tertiaryPower(erp_client, tariff, contract_id):
    """
    Terciary Power:
     {
        "P1": 20000,
        "P2": 20000,
        "P3": 20000
    }
    """
    if '2.' in tariff:
        return {}
    period_obj = erp_client.model('giscedata.polissa.potencia.contractada.periode')
    period_powers = period_obj.read([('polissa_id', '=', contract_id)])
    return {
     'P{}'.format(i): int(period['potencia'] * 1000) for i, period in enumerate(period_powers, 1)
    }


def get_devices(erp_client, device_ids):
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
    if not device_ids:
        return []
    compt_obj = erp_client.model('giscedata.lectures.comptador')
    fields = ['data_alta', 'data_baixa']

    devices = []
    for comptador in compt_obj.read(device_ids, fields) or []:
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


def get_contract_address(erp_client, cups_id):
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
    cups_obj = erp_client.model('giscedata.cups.ps')
    muni_obj = erp_client.model('res.municipi')
    state_obj = erp_client.model('res.country.state')
    sips_obj = erp_client.model('giscedata.sips.ps')

    cups_fields = ['id_municipi', 'tv', 'nv', 'cpa', 'cpo', 'pnp', 'pt',
                   'name', 'es', 'pu', 'dp']
    cups = cups_obj.read(cups_id, cups_fields)
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


def get_building_details(erp_client, building_id):
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
    if not building_id:
        return None

    building_obj = erp_client.model('empowering.cups.building')

    fields_to_read = [
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
    building = building_obj.read(building_id)[0]
    return {field: building[field] for field in fields_to_read}


def get_eprofile(erp_client, profile_id):
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
    if not profile_id:
        return None

    profile_obj = erp_client.model('empowering.modcontractual.profile')
    profile = profile_obj.read(profile_id)
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


def get_cups_to_climaticZone(erp_client, cups_id):
    """
    Climatic zone from CTE DB-HE:
    """
    if not cups_id:
        return None
    cups_obj = erp_client.model('giscedata.cups.ps')
    muni_obj = erp_client.model('res.municipi')
    cups = cups_obj.read(cups_id, ['id_municipi'])
    ine = muni_obj.read(cups['id_municipi'][0], ['ine'])['ine']
    if ine in ine_to_zc.keys():
        return ine_to_zc[ine]


def get_service(erp_client, service_id):
    """
    Convert service
     {
        "OT701": "p1;P2;px"
     }
    """
    if not service_id:
        return {}

    service_obj = erp_client.model('empowering.modcontractual.service')
    service = service_obj.read(service_id)
    fields_to_read = [
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
    return {field: service[field] for field in fields_to_read}


def get_version(erp_client, modcontract_id):
    """
    Get active contract modification's name
    int
    """
    modcontract_obj = erp_client.model('giscedata.polissa.modcontractual')
    version = modcontract_obj.read(modcontract_id)
    return int(version['name'])


def get_report(erp_client, date_start, partner_id):
    """
    Report.
    {
        "language": "ca_ES",
        "initialMonth": "201701"
    }
    """
    partner_obj = erp_client.model('res.partner')
    partner = partner_obj.read(partner_id, ['lang'])

    initial_month = datetime.strptime(date_start, '%Y-%m-%d').strftime('%Y%m')
    return {
        'language': partner['lang'],
        'initialMonth': int(initial_month),
    }


def get_experimentalgroup(erp_client, cups_id):
    """
    If a contract has empowering return True, False otherwise
    """
    cups_obj = erp_client.model('giscedata.cups.ps')
    cups = cups_obj.read(cups_id)
    return cups.get('empowering', False)
