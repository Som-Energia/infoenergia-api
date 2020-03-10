import functools

from sanic.log import logger

from infoenergia_api.tasks import get_devices, get_f1_energy_measurements, get_f1_power
from infoenergia_api.utils import get_request_filters, make_utc_timestamp, make_uuid


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
    id_invoices = factura_obj.search(filters)
    return factura_obj.read(id_invoices) or []


async def async_get_invoices(request, id_contract=None):
    try:
        result = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_invoices, request, id_contract)
        )

    except Exception as e:
        raise e
    return result


async def async_get_f1_measures_json(loop, executor, erp_client, sem, invoices):
    async with sem:
        result = await loop.run_in_executor(
            executor,
            functools.partial(get_f1_measures_json, erp_client, invoices)
        )
    return result
