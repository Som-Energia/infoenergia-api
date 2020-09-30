import functools
from datetime import date

from ..utils import get_juridic_filter, get_contract_user_filters


def get_modcontracts(request):
    modcon_obj = request.app.erp_client.model('giscedata.polissa.modcontractual')
    contract_obj = request.app.erp_client.model('giscedata.polissa')

    filters = [
        ('tipus', '=', 'mod'),
        ('polissa_id.empowering_profile_id', '=', 1),
        ('data_inici', '>=', request.args.get('from_', str(date.today())))
    ]

    filters = get_contract_user_filters(request, filters)

    if 'to_' in request.args:
        filters.append(('data_inici', '<=', request.args['to_'][0]))

    if 'juridic_type' in request.args:
        filters += get_juridic_filter(
            request.app.erp_client,
            request.args['juridic_type'][0],
        )
    if 'type' in request.args:
        if request.args['type'][0] == 'canceled':
            filters.append(('state', '=', 'baixa'))
        else:
            filters.extend([('active', '=', True), ('state', '=', 'actiu')])
    modcontract_ids = modcon_obj.search(filters, context={'active_test': False})
    contracts_ids = contract_obj.search([('modcontractual_activa', 'in', modcontract_ids)], context={'active_test': False})
    return contracts_ids


async def async_get_modcontracts(request, id_contract=None):
    try:
        result = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_modcontracts, request)
        )
    except Exception as e:
        raise e
    return result
