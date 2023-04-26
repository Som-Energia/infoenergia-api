import asyncio
from datetime import timedelta
import pytz
from somutils import isodates
from psycopg import AsyncClientCursor

from ..utils import (
    make_uuid,
    get_contract_id,
    iso_format,
    iso_format_tz,
    increment_isodate,
    local_isodate_2_naive_local_datetime,
    local_isodate_2_utc_isodatetime,
    naive_local_isodatetime_2_utc_datetime,
    naive_utc_datetime_2_utc_datetime,
)
from ..tasks import get_cups
from .erp import get_erp_instance
from .mongo_manager import get_mongo_instance
from .erpdb_manager import get_erpdb_instance

def cch_date_from_cch_datetime(cch, measure_delta):
    utcdatetime = naive_local_isodatetime_2_utc_datetime(
        naive_local_isodate = cch['datetime'],
        is_dst = cch['season'],
    )
    utcdatetime -= timedelta(**measure_delta)
    return iso_format_tz(utcdatetime)

def cch_date_from_cch_utctimestamp(raw_data, measure_delta):
    utcdatetime = naive_utc_datetime_2_utc_datetime(
        naive_utc_datetime=raw_data['utc_timestamp'],
    )
    utcdatetime -= timedelta(**measure_delta)
    return iso_format_tz(utcdatetime)

class CurveRepository():
    extra_filter = dict()
    measure_delta = dict(hours=1)
    translated_fields=dict()

    def measurements(self, raw_data):
        return dict(
            (
                self.translated_fields.get(field, field),
                raw_data[field],
            )
            for field in self.fields
        )

class MongoCurveRepository(CurveRepository):

    def __init__(self):
        mongo_client = get_mongo_instance()
        self.db = mongo_client.somenergia

    def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        downloaded_from=None,
        downloaded_to=None,
        **extra_filter
    ):
        query = {}
        if start:
            query.setdefault('datetime', {}).update(
                {"$gte": local_isodate_2_naive_local_datetime(start)}
            )
        if end:
            query.setdefault('datetime', {}).update(
                {"$lte": local_isodate_2_naive_local_datetime(increment_isodate(end))}
            )
        if downloaded_from:
            query.setdefault('create_at', {}).update(
                {"$gte": local_isodate_2_naive_local_datetime(downloaded_from)}
            )
        if downloaded_to:
            query.setdefault('create_at', {}).update(
                {"$lte": local_isodate_2_naive_local_datetime(downloaded_to)}
            )
        for key, value in extra_filter.items():
            query.update({key: {"$eq": value}})
        if cups:
            query.update(name={"$regex": "^{}".format(cups[:20])})
        return query

    async def get_curve(self, start, end, cups=None):
        query = self.build_query(start, end, cups, **self.extra_filter)
        cch_collection = self.db[self.model]

        def cch_transform(cch):
            return dict(cch,
                id=int(cch['id']), # un-bson-ize
                date=cch_date_from_cch_datetime(cch, self.measure_delta),
                dateDownload=iso_format(cch["create_at"]),
                dateUpdate=iso_format(cch["update_at"]),
            )

        result = [
            cch_transform(cch)
            async for cch in cch_collection.find(
                filter=query,
                # exclude _id since it is not serializable
                projection=dict(_id=False),
                #sort=[( "datetime", 1 )],
            )
        ]
        return result


class TimescaleCurveRepository(CurveRepository):

    async def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        downloaded_from=None,
        downloaded_to=None,
        **extra_filter
    ):
        erpdb = await get_erpdb_instance()
        async with AsyncClientCursor(erpdb) as cursor:
            result = []
            if cups:
                result += [cursor.mogrify("name ILIKE %s", [cups[:20]+"%"])]
            if start:
                start_utc = local_isodate_2_utc_isodatetime(start)
                result += [cursor.mogrify("utc_timestamp >= %s",
                    [start_utc]
                )]
            if end:
                end_utc = local_isodate_2_utc_isodatetime(increment_isodate(end))
                result += [cursor.mogrify("utc_timestamp <= %s",
                    [end_utc]
                )]
            if downloaded_from:
                result += [cursor.mogrify("create_at >= %s", [downloaded_from+" 00:00:00"])]
            if downloaded_to:
                result += [cursor.mogrify("create_at <= %s", [downloaded_to+" 00:00:00"])]
            for key, value in extra_filter.items():
                result += [cursor.mogrify(f"{key} = %s", [value])]

        return result

    async def get_curve(self, start, end, cups=None):

        def cch_transform(cch):
            return dict(cch,
                date=cch_date_from_cch_utctimestamp(cch, self.measure_delta),
                dateDownload=iso_format(cch["create_at"]),
                dateUpdate=iso_format(cch["update_at"]),
                datetime=iso_format(cch["datetime"]),
                utc_timestamp=iso_format(cch["utc_timestamp"]),

            )
        from psycopg.rows import dict_row
        query = await self.build_query(start, end, cups, **self.extra_filter)

        erpdb = await get_erpdb_instance()
        async with AsyncClientCursor(erpdb, row_factory=dict_row) as cursor:
            await cursor.execute(f"""
                SELECT * from {self.model} WHERE {" AND ".join(query) or "TRUE"};
            """)
            return [
                cch_transform(cch) for cch in await cursor.fetchall()
            ]

#### Concrete curves

class TgCchF1Repository(TimescaleCurveRepository):

    model = 'tg_f1'
    fields = [
        'season',
        'ai',
        'ao',
        'r1',
        'r2',
        'r3',
        'r4',
        'source',
        'validated',
        'date',
        'dateDownload',
        'dateUpdate',
        'reserve1',
        'reserve2',
        'datetime',
        'measure_type',
        'utc_timestamp',
    ]
    translated_fields = dict(
        measure_type='measureType',
    )


class TgCchF5dRepository(MongoCurveRepository):
    model = 'tg_cchfact'
    fields = [
        'date',
        'season',
        'dateDownload',
        'dateUpdate',
        'source',
        'validated',
        'ai',
        'ao',
        'r1',
        'r2',
        'r3',
        'r4',
    ]

class TgCchValRepository(MongoCurveRepository):
    model = "tg_cchval"
    fields=[
        'date',
        'season',
        'dateDownload',
        'dateUpdate',
        'ai',
        'ao',
    ]

class TgCchPnRepository(MongoCurveRepository):
    model = "tg_p1"
    fields = [
        "date",
        "season",
        'dateDownload',
        'dateUpdate',
        "source",
        "validated",
        "type",
        "measure_type",
        "ai",
        "ao",
        "reserve1",
        "reserve2",
        "r1",
        "r2",
        "r3",
        "r4",
        "aiquality",
        "aoquality",
        "reserve1quality",
        "reserve2quality",
        "r1quality",
        "r2quality",
        "r3quality",
        "r4quality",
    ]
    translated_fields = dict(
        measure_type='measureType',
        #aiquality='aiQuality', # TODO: aiquality not translated, bug?
        aoquality='aoQuality',
        reserve1quality='reserve1Quality',
        reserve2quality='reserve2Quality',
        r1quality='r1Quality',
        r2quality='r2Quality',
        r3quality='r3Quality',
        r4quality='r4Quality',
    )

class TgCchP1Repository(TgCchPnRepository):
    extra_filter = dict(
        type='p',
    )

class TgCchP2Repository(TgCchPnRepository):
    extra_filter = dict(
        type='p4',
    )
    measure_delta=dict(minutes=15)

class TgCchGennetabetaRepository(MongoCurveRepository):
    model='tg_cch_gennetabeta'
    fields=[
        "date",
        'ae',
        'ai',
        'bill',
        'dateDownload',
        'dateUpdate',
        'r1',
        'r2',
        'r3',
        'r4',
        'season',
        'source',
        'validated',
    ]

class TgCchAutoconsRepository(MongoCurveRepository):
    model='tg_cch_autocons'
    fields = [
        'date',
        'ae',
        'ai',
        'bill',
        'dateDownload',
        'dateUpdate',
        'r1',
        'r2',
        'r3',
        'r4',
        'season',
        'source',
        'validated',
    ]


migrated_repositories={
    'tg_cchfact': TgCchF5dRepository,
    'tg_cchval': TgCchValRepository,
    'P1': TgCchP1Repository,
    'P2': TgCchP2Repository,
    "tg_f1": TgCchF1Repository,
    'tg_gennetabeta': TgCchGennetabetaRepository,
    'tg_cchautocons': TgCchAutoconsRepository,
}

def create_repository(curve_type):
    return migrated_repositories[curve_type]()

async def get_curve(type, start, end, cups=None):
    repository=create_repository(type)
    return await repository.get_curve(start, end, cups=cups)


async def get_measures(curve_type, cch, contract_id, user):
    loop = asyncio.get_running_loop()

    if not contract_id:
        contract_id = await loop.run_in_executor(
            None,
            get_contract_id,
            get_erp_instance(),
            cch['name'],
            user,
        )
    if not contract_id:
        return {}

    repository = create_repository(curve_type)
    return {
        "contractId": contract_id,
        "meteringPointId": make_uuid("giscedata.cups.ps", cch['name']),
        "measurements": repository.measurements(cch),
    }

async def async_get_cch(request, contract_id=None):
    loop = asyncio.get_running_loop()
    filters = dict(request.query_args)
    cups = None

    if contract_id:
        cups = await loop.run_in_executor(None, get_cups, request.ctx.user, contract_id)
        if not cups:
            return []
            raise Exception("Contract not availble")

    curve_type = filters.get("type")
    result = await get_curve(
        curve_type,
        start = filters.get('from_', None),
        end = filters.get('to_', None),
        cups = cups,
    )
    return result
