import functools

from sanic.log import logger

from ..tasks import (get_building_details, get_contract_address,
                     get_cups_to_climaticZone, get_current_power,
                     get_current_tariff, get_devices, get_eprofile,
                     get_experimentalgroup, get_id_for_contract,
                     get_powerHistory, get_report, get_service,
                     get_tariffHistory, get_tertiaryPower, get_version)
from ..utils import get_request_filters, make_utc_timestamp, make_uuid


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
        filters = get_request_filters(
            request.app.erp_client,
            request,
            filters,
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


async def async_get_contract_json(loop, executor, erp_client, sem, contract):
    async with sem:
        result = await loop.run_in_executor(
            executor,
            functools.partial(get_contract_json, erp_client, contract)
        )
    return result
