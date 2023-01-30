import uuid
from datetime import datetime
import pytz

from .api.registration.models import UserCategory


def make_uuid(model, model_id):
    token = "%s,%s" % (model, model_id)
    return str(uuid.uuid5(uuid.NAMESPACE_OID, token))


def make_timestamp(date):
    if not date:
        return None
    tz = pytz.timezone("Europe/Madrid")
    datetime_obj = datetime.strptime(date, "%Y-%m-%d")
    return tz.localize(datetime_obj).isoformat("T")

def iso_format(date):
    """Format a date in naive iso format"""
    return date.strftime("%Y-%m-%d %H:%M:%S")

def iso_format_tz(date):
    """Format a date in tz aware iso format"""
    return date.strftime("%Y-%m-%d %H:%M:%S%z")


def get_id_for_contract(obj, modcontract_ids):
    ids = (obj.search([("modcontractual_id", "=", ids)]) for ids in modcontract_ids)
    wanted_id = next((wanted_id[0] for wanted_id in ids if wanted_id), None)
    return wanted_id


def get_request_filters(erp_client, request, filters):
    if "juridic_type" in request.args:
        filters += get_juridic_filter(
            erp_client,
            request.args["juridic_type"][0],
        )
    if "tariff" in request.args:
        tariff_type = erp_client.model("giscedata.polissa.tarifa")
        tariff = tariff_type.search([("name", "=", request.args["tariff"][0])])
        if "contracts" in request.endpoint:
            filters += [("tarifa", "=", tariff[0])]
        elif "f1" in request.endpoint:
            filters += [("tarifa_acces_id", "=", tariff[0])]
        elif "tariff" in request.endpoint:
            filters += [("name", "=", request.args["tariff"][0])]
    if "from_" in request.args:
        if "contracts" in request.endpoint:
            filters += [("data_alta", ">=", request.args["from_"][0])]
        elif "f1" in request.endpoint:
            filters += [("data_inici", ">=", request.args["from_"][0])]
    if "to_" in request.args:
        if "contracts" in request.endpoint:
            filters += [("data_alta", "<=", request.args["to_"][0])]
        elif "f1" in request.endpoint:
            filters += [("data_inici", "<=", request.args["to_"][0])]
    return filters


def get_erp_category(erp_client, user):
    if user.category == UserCategory.ENERGETICA.value:
        category_id = erp_client.model("res.partner.category").search(
            [("name", "=", UserCategory.ENERGETICA.value), ("active", "=", True)]
        )
        return category_id


def get_contract_user_filters(erp_client, user, filters):
    category_id = get_erp_category(erp_client, user)
    if category_id:
        filters += [("soci.category_id", "=", category_id)]

    return filters


def get_invoice_user_filters(erp_client, user, filters):
    category_id = get_erp_category(erp_client, user)
    if category_id:
        filters += [("polissa_id.soci.category_id", "=", category_id)]

    return filters


def get_juridic_filter(erp_client, juridic_type):
    person_type = erp_client.model("res.partner")
    if juridic_type == "physical_person":
        physical_person = person_type.search(
            [
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                "&",
                ("vat", "not ilike", "ESA"),
                ("vat", "not ilike", "ESB"),
                ("vat", "not ilike", "ESC"),
                ("vat", "not ilike", "ESD"),
                ("vat", "not ilike", "ESE"),
                ("vat", "not ilike", "ESF"),
                ("vat", "not ilike", "ESH"),
                ("vat", "not ilike", "ESJ"),
                ("vat", "not ilike", "ESN"),
                ("vat", "not ilike", "ESP"),
                ("vat", "not ilike", "ESQ"),
                ("vat", "not ilike", "ESR"),
                ("vat", "not ilike", "ESS"),
                ("vat", "not ilike", "ESU"),
                ("vat", "not ilike", "ESV"),
                ("vat", "not ilike", "ESW"),
            ]
        )
        juridic_filters = [("titular", "in", physical_person), ("cnae", "=", 986)]
    else:
        juridic_person = person_type.search(
            [
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                "|",
                ("vat", "ilike", "ESA"),
                ("vat", "ilike", "ESB"),
                ("vat", "ilike", "ESC"),
                ("vat", "ilike", "ESD"),
                ("vat", "ilike", "ESE"),
                ("vat", "ilike", "ESF"),
                ("vat", "ilike", "ESH"),
                ("vat", "ilike", "ESJ"),
                ("vat", "ilike", "ESN"),
                ("vat", "ilike", "ESP"),
                ("vat", "ilike", "ESQ"),
                ("vat", "ilike", "ESR"),
                ("vat", "ilike", "ESS"),
                ("vat", "ilike", "ESU"),
                ("vat", "ilike", "ESV"),
                ("vat", "ilike", "ESW"),
            ]
        )
        juridic_filters = [("titular", "in", juridic_person)]

    return juridic_filters


async def get_cch_query(filters, cups):
    query = {}
    if "from_" in filters:
        query.update(
            {"datetime": {"$gte": datetime.strptime(filters["from_"][0], "%Y-%m-%d")}}
        )

    if "to_" in filters:
        datetime_query = query.get("datetime", {})
        datetime_query.update(
            {"$lte": datetime.strptime(filters["to_"][0], "%Y-%m-%d")}
        )
        query["datetime"] = datetime_query

    if "downloaded_from" in filters:
        query.update(
            {
                "create_at": {
                    "$gte": datetime.strptime(filters["downloaded_from"][0], "%Y-%m-%d")
                }
            }
        )

    if "downloaded_to" in filters:
        create_at_query = query.get("create_at", {})
        create_at_query.update(
            {"$lte": datetime.strptime(filters["downloaded_to"][0], "%Y-%m-%d")}
        )
        query["create_at"] = create_at_query

    if "P1" in filters["type"][0].upper():
        query.update({"type": {"$eq": "p"}})

    if "P2" in filters["type"][0].upper():
        query.update({"type": {"$eq": "p4"}})

    if cups:
        query.update({"name": {"$regex": "^{}".format(cups[0][:20])}})

    return query


def get_contract_id(erp_client, cups, user):
    contract_obj = erp_client.model("giscedata.polissa")

    filters = [
        ("active", "=", True),
        ("state", "=", "activa"),
        ("emp_allow_send_data", "=", True),
        ("cups.name", "=", cups),
    ]
    filters = get_contract_user_filters(erp_client, user, filters)
    contract = contract_obj.search(filters)
    if not contract:
        filters += [("cups.name", "ilike", cups[:20])]
        contract = contract_obj.search(filters)
    if contract:
        return contract_obj.read(contract, ["name"])[0]["name"]
