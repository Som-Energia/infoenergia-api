import functools
from datetime import date

from ..utils import get_juridic_filter, get_invoice_user_filters


def get_modcontracts(request, contractId=None):
    modcon_obj = request.app.erp_client.model('giscedata.polissa.modcontractual')
    contract_obj = request.app.erp_client.model('giscedata.polissa')

    filters = [
        ('polissa_id.empowering_profile_id', '=', 1),
    ]
    filters = get_invoice_user_filters(
        request.app.erp_client, request.ctx.user, filters
    )

    if 'juridic_type' in request.args:
        filters += get_juridic_filter(
            request.app.erp_client,
            request.args['juridic_type'][0],
        )

    if request.args['type'][0] == 'canceled':
        filters.extend([
            ('polissa_id.state', '=', 'baixa'),
            ('data_final', '>=', request.args.get('from_', str(date.today()))),
            ('data_final', '<=', request.args['to_'][0])
        ])
    else:
        filters.extend([
            ('active', '=', True),
            ('state', '=', 'actiu'),
            ('tipus', '=', 'mod'),
            ('data_inici', '>=', request.args.get('from_', str(date.today()))),
            ('data_inici', '<=', request.args['to_'][0])
        ])

    modcontract_ids = modcon_obj.search(filters, context={'active_test': False})

    filter_mods = [('modcontractual_activa', 'in', modcontract_ids)]

    if contractId:
        filter_mods.append(('name', '=', contractId))

    contracts_ids = contract_obj.search(filter_mods, context={'active_test': False})
    return contracts_ids


async def async_get_modcontracts(request, id_contract=None):
    try:
        result = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_modcontracts, request, id_contract)
        )
    except Exception as e:
        raise e
    return result
