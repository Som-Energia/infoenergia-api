import functools

from sanic.log import logger

from ..tasks import (get_building_details, get_contract_address,
                     get_cups_to_climaticZone, get_current_power,
                     get_current_tariff, get_devices, get_eprofile,
                     get_experimentalgroup, get_powerHistory, get_report,
                     get_service, get_tariffHistory, get_tertiaryPower,
                     get_version)
from ..utils import get_juridic_filter



def get_modcontracts(request):
    modcon_obj =  request.app.erp_client.model('giscedata.polissa.modcontractual')
    contract_obj = request.app.erp_client.model('giscedata.polissa')

    fields4contracts = [
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

    filters = [
        ('tipus', '=', 'mod'),
        ('polissa_id.empowering_profile_id', '=', 1),
        ('data_inici', '>=', request.args['from_'][0])
    ]

    if 'to_' in request.args:
        filters.append(('data_inici', '<=', request.args['to_'][0]))

    if 'juridic_type' in request.args:
        filters += get_juridic_filter(
            request.args['juridic_type'][0],
        )
    if 'type' in request.args:
        if request.args['type'][0] == 'canceled':
            filters.append(('state', '=', 'baixa'))
        else:
            filters.extend([('active', '=', True), ('state', '=', 'actiu')])
    modcontract_ids = modcon_obj.search(filters, context={'active_test': False})
    id_contracts = contract_obj.search([('modcontractual_activa', 'in', modcontract_ids)], context={'active_test': False})
    return contract_obj.read(id_contracts, fields4contracts) or []


async def async_get_modcontracts(request):
    try:
        result = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_modcontracts, request)
        )
    except Exception as e:
        raise e
    return result