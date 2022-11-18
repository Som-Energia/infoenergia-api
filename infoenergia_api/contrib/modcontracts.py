import functools
from datetime import date

from ..utils import get_juridic_filter, get_invoice_user_filters


def get_modcontracts(request, contract_id=None):
    modcon_obj = request.app.ctx.erp_client.model("giscedata.polissa.modcontractual")
    contract_obj = request.app.ctx.erp_client.model("giscedata.polissa")

    filters = [
        ("polissa_id.emp_allow_send_data", "=", True),
    ]
    filters = get_invoice_user_filters(
        request.app.ctx.erp_client, request.ctx.user, filters
    )
    if "juridic_type" in request.args:
        filters += get_juridic_filter(
            request.app.ctx.erp_client,
            request.args["juridic_type"][0],
        )

    if "type" in request.args and request.args["type"][0] == "canceled":
        filters.extend(
            [
                ("polissa_id.state", "=", "baixa"),
                ("data_final", ">=", request.args.get("from_", str(date.today()))),
                ("data_final", "<=", request.args.get("to_", str(date.today()))),
            ]
        )
    else:
        filters.extend(
            [
                ("active", "=", True),
                ("state", "=", "actiu"),
                ("tipus", "=", "mod"),
                ("data_inici", ">=", request.args.get("from_", str(date.today()))),
                ("data_inici", "<=", request.args.get("to_", str(date.today()))),
            ]
        )

    modcontract_ids = modcon_obj.search(filters, context={"active_test": False})

    filter_mods = [("modcontractual_activa", "in", modcontract_ids)]

    if contract_id:
        filter_mods.append(("name", "=", contract_id))

    contracts_ids = contract_obj.search(filter_mods, context={"active_test": False})
    return contracts_ids


async def async_get_modcontracts(request, id_contract=None):
    try:
        result = await request.app.loop.run_in_executor(
            None,
            functools.partial(get_modcontracts, request, id_contract),
        )
    except Exception as e:
        raise
    return result
