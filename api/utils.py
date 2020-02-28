import uuid
from datetime import datetime

from pytz import timezone


def make_uuid(model, model_id):
    token = '%s,%s' % (model, model_id)
    return str(uuid.uuid5(uuid.NAMESPACE_OID, token))


def make_utc_timestamp(timestamp):
    if not timestamp:
        return None
    datetime_obj = datetime.strptime(timestamp, '%Y-%m-%d')
    datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('Europe/Madrid'))
    return datetime_obj_utc.isoformat('T') + 'Z'


def get_id_for_contract(obj, modcontract_ids):
    ids = (
        obj.search([('modcontractual_id', '=', ids)])
        for ids in modcontract_ids
    )
    wanted_id = next(
        (wanted_id[0] for wanted_id in ids if wanted_id),
        None
    )
    return wanted_id


def get_request_filters(erp_client, request, filters):
    if 'juridic_type' in request.args:
        filters += get_juridic_filter(
            request.args['juridic_type'][0],
        )
    if 'tariff' in request.args:
        tariff_type = erp_client.model('giscedata.polissa.tarifa')
        tariff = tariff_type.search(
            [
                ('name', '=', request.args['tariff'][0])
            ]
        )
        if 'contracts' in request.endpoint:
            filters += [('tarifa', '=', tariff[0])]
        elif 'f1' in request.endpoint:
            filters += [('tarifa_acces_id', '=', tariff[0])]
    if 'from_' in request.args:
        if 'contracts' in request.endpoint:
            filters += [
                ('data_alta', '>=', request.args['from_'][0])
            ]
        elif 'f1' in request.endpoint:
            filters += [
                ('data_inici', '>=', request.args['from_'][0])
            ]
    if 'to_' in request.args:
        if 'contracts' in request.endpoint:
            filters += [
                ('data_alta', '<=', request.args['from_'][0])
            ]
        elif 'f1' in request.endpoint:
            filters += [
                ('data_inici', '<=', request.args['from_'][0])
            ]
    return filters


def get_juridic_filter(juridic_type):
    if juridic_type == 'physical_person':
        juridic_filters = [
            '&',
            '!', ('titular_nif', 'ilike', 'ESA'),
            '!', ('titular_nif', 'ilike', 'ESB'),
            '!', ('titular_nif', 'ilike', 'ESC'),
            '!', ('titular_nif', 'ilike', 'ESD'),
            '!', ('titular_nif', 'ilike', 'ESE'),
            '!', ('titular_nif', 'ilike', 'ESF'),
            '!', ('titular_nif', 'ilike', 'ESH'),
            '!', ('titular_nif', 'ilike', 'ESJ'),
            '!', ('titular_nif', 'ilike', 'ESN'),
            '!', ('titular_nif', 'ilike', 'ESP'),
            '!', ('titular_nif', 'ilike', 'ESQ'),
            '!', ('titular_nif', 'ilike', 'ESR'),
            '!', ('titular_nif', 'ilike', 'ESS'),
            '!', ('titular_nif', 'ilike', 'ESU'),
            '!', ('titular_nif', 'ilike', 'ESV'),
            '!', ('titular_nif', 'ilike', 'ESW'),
            ('cnae', '=', 986)
        ]
    else:
        juridic_filters = [
            '|',
            ('titular_nif', 'ilike', 'ESA'),
            ('titular_nif', 'ilike', 'ESB'),
            ('titular_nif', 'ilike', 'ESC'),
            ('titular_nif', 'ilike', 'ESD'),
            ('titular_nif', 'ilike', 'ESE'),
            ('titular_nif', 'ilike', 'ESF'),
            ('titular_nif', 'ilike', 'ESH'),
            ('titular_nif', 'ilike', 'ESJ'),
            ('titular_nif', 'ilike', 'ESN'),
            ('titular_nif', 'ilike', 'ESP'),
            ('titular_nif', 'ilike', 'ESQ'),
            ('titular_nif', 'ilike', 'ESR'),
            ('titular_nif', 'ilike', 'ESS'),
            ('titular_nif', 'ilike', 'ESU'),
            ('titular_nif', 'ilike', 'ESV'),
            ('titular_nif', 'ilike', 'ESW'),
        ]

    return juridic_filters
