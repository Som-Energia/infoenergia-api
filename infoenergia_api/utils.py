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
            erp_client,
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
                ('data_alta', '<=', request.args['to_'][0])
            ]
        elif 'f1' in request.endpoint:
            filters += [
                ('data_inici', '<=', request.args['to_'][0])
            ]
    return filters


def get_juridic_filter(erp_client, juridic_type):
    person_type = erp_client.model('res.partner')
    if juridic_type == 'physical_person':
        physical_person = person_type.search([
            '&','&','&', '&','&','&', '&','&','&', '&','&','&', '&','&','&',
            ('vat', 'not ilike', 'ESA'),
            ('vat', 'not ilike', 'ESB'),
            ('vat', 'not ilike', 'ESC'),
            ('vat', 'not ilike', 'ESD'),
            ('vat', 'not ilike', 'ESE'),
            ('vat', 'not ilike', 'ESF'),
            ('vat', 'not ilike', 'ESH'),
            ('vat', 'not ilike', 'ESJ'),
            ('vat', 'not ilike', 'ESN'),
            ('vat', 'not ilike', 'ESP'),
            ('vat', 'not ilike', 'ESQ'),
            ('vat', 'not ilike', 'ESR'),
            ('vat', 'not ilike', 'ESS'),
            ('vat', 'not ilike', 'ESU'),
            ('vat', 'not ilike', 'ESV'),
            ('vat', 'not ilike', 'ESW')
        ])
        juridic_filters = [('titular', 'in', physical_person), ('cnae', '=', 986)]
    else:
        juridic_person = person_type.search([
            '|','|','|', '|','|','|', '|','|','|', '|','|','|', '|','|','|',
            ('vat', 'ilike', 'ESA'),
            ('vat', 'ilike', 'ESB'),
            ('vat', 'ilike', 'ESC'),
            ('vat', 'ilike', 'ESD'),
            ('vat', 'ilike', 'ESE'),
            ('vat', 'ilike', 'ESF'),
            ('vat', 'ilike', 'ESH'),
            ('vat', 'ilike', 'ESJ'),
            ('vat', 'ilike', 'ESN'),
            ('vat', 'ilike', 'ESP'),
            ('vat', 'ilike', 'ESQ'),
            ('vat', 'ilike', 'ESR'),
            ('vat', 'ilike', 'ESS'),
            ('vat', 'ilike', 'ESU'),
            ('vat', 'ilike', 'ESV'),
            ('vat', 'ilike', 'ESW')
        ])
        juridic_filters = [('titular', 'in', juridic_person)]


    return juridic_filters


def get_cch_filters(request, filters):
    if {'to_','from_'} <= request.args.keys():
        filters.update({"datetime" : {
            "$gt":
                datetime.strptime(request.args['from_'][0],"%Y-%m-%d"),
            "$lt":
                datetime.strptime(request.args['to_'][0],"%Y-%m-%d")
            }})
    if 'from_' in request.args:
        filters.update({"datetime" : {"$gt":
            datetime.strptime(request.args['from_'][0],"%Y-%m-%d")}})

    if 'to_' in request.args:
        filters.update({"datetime" : {"$lt":
            datetime.strptime(request.args['to_'][0],"%Y-%m-%d")}})


    return filters
