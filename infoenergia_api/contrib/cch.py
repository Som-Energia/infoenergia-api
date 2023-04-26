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
)
from ..tasks import get_cups
from .erp import get_erp_instance
from .mongo_manager import get_mongo_instance
from .erpdb_manager import get_erpdb_instance


class CurveRepository():
    extra_filter = dict()
    measure_delta = dict(hours=1)


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

        def cch_tz_isodate(cch):
            tz = pytz.timezone("Europe/Madrid")
            date_cch = tz.localize(cch['datetime'], is_dst=cch['season']).astimezone(pytz.utc)
            date_cch -= timedelta(**self.measure_delta)
            return iso_format_tz(date_cch)

        def cch_transform(cch):
            return dict(cch,
                id=int(cch['id']), # un-bson-ize
                date=cch_tz_isodate(cch),
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


class ErpMongoCurveRepository(CurveRepository):

    def __init__(self):
        self._erp = get_erp_instance()

    def to_filter(self, end):
        return [('datetime', '<=', increment_isodate(end))]

    def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        downloaded_from=None,
        downloaded_to=None,
        **extra_filter
    ):
        result = []
        if start:
            result += [('datetime', '>=', start)]

        if end:
            result += self.to_filter(end)

        if downloaded_from:
            result += [('create_at', '>=', downloaded_from)]

        if downloaded_to:
            result += [('create_at', '<=', downloaded_to)]

        if cups:
            # Not using ilike because ERP model turns it into
            # into '=' anyway, see the erp code
            result += [('name', '=', cups)]

        return result

    async def get_curve(self, start, end, cups=None):
        loop = asyncio.get_running_loop()
        query = self.build_query(start, end, cups, **self.extra_filter)
        erp_model_name = self.model.replace('_','.',1)
        if not hasattr(self, 'erp_model'):
            self.erp_model = self._erp.model(erp_model_name)
        cch_ids = await loop.run_in_executor(None, self.erp_model.search, query)
        cchs = await loop.run_in_executor(None, self.erp_model.read, cch_ids)

        def erp_cch_tz_isodate(cch):
            tz = pytz.timezone("Europe/Madrid")
            localtime = isodates.parseLocalTime(cch['datetime'], isSummer=cch['season'])
            date_cch -= timedelta(**self.measure_delta)
            return iso_format_tz(localtime.astimezone(tz))

        def cch_transform(cch):
            return dict(cch,
                date=erp_cch_tz_isodate(cch),
            )

        return [
            cch_transform(cch) for cch in cchs
        ]


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

        def date_cch(raw_data):
            _utc_timestamp = raw_data['utc_timestamp'].replace(tzinfo=pytz.UTC)
            _utc_timestamp -= timedelta(**self.measure_delta)
            return iso_format_tz(_utc_timestamp)

        def cch_transform(cch):
            return dict(cch,
                date=date_cch(cch),
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

    def measurements(self, raw_data):
        return dict(
            season=raw_data['season'],
            ai=raw_data['ai'],
            ao=raw_data['ao'],
            r1=raw_data['r1'],
            r2=raw_data['r2'],
            r3=raw_data['r3'],
            r4=raw_data['r4'],
            source=raw_data['source'],
            validated=raw_data['validated'],
            date=raw_data['date'],
            dateDownload=raw_data['dateDownload'],
            dateUpdate=raw_data['dateUpdate'],
            reserve1=raw_data['reserve1'],
            reserve2=raw_data['reserve2'],
            measureType=raw_data['measure_type'],
            datetime=raw_data['datetime'],
            utc_timestamp=raw_data['utc_timestamp'],
        )




class TgCchF5dRepository(MongoCurveRepository):
    model = 'tg_cchfact'

    def measurements(self, raw_data):
        return dict(
            date=raw_data['date'],
            season=raw_data['season'],
            dateDownload=raw_data['dateDownload'],
            dateUpdate=raw_data['dateUpdate'],
            source=raw_data['source'],
            validated=raw_data['validated'],
            ai=raw_data['ai'],
            ao=raw_data['ao'],
            r1=raw_data['r1'],
            r2=raw_data['r2'],
            r3=raw_data['r3'],
            r4=raw_data['r4'],
        )

class TgCchValRepository(MongoCurveRepository):
    model = "tg_cchval"

    def measurements(self, raw_data):
        return dict(
            date=raw_data["date"],
            season=raw_data["season"],
            dateDownload=raw_data['dateDownload'],
            dateUpdate=raw_data['dateUpdate'],
            ai=raw_data["ai"],
            ao=raw_data["ao"],
        )

class TgCchPnRepository(MongoCurveRepository):
    model = "tg_p1"

    def measurements(self, raw_data):
        return dict(
            date=raw_data["date"],
            season=raw_data["season"],
            dateDownload=raw_data['dateDownload'],
            dateUpdate=raw_data['dateUpdate'],
            source=raw_data["source"],
            validated=raw_data["validated"],
            type=raw_data["type"],
            measureType=raw_data["measure_type"],
            ai=raw_data["ai"],
            ao=raw_data["ao"],
            reserve1=raw_data["reserve1"],
            reserve2=raw_data["reserve2"],
            r1=raw_data["r1"],
            r2=raw_data["r2"],
            r3=raw_data["r3"],
            r4=raw_data["r4"],
            aiquality=raw_data["aiquality"],
            aoQuality=raw_data["aoquality"],
            reserve1Quality=raw_data["reserve1quality"],
            reserve2Quality=raw_data["reserve2quality"],
            r1Quality=raw_data["r1quality"],
            r2Quality=raw_data["r2quality"],
            r3Quality=raw_data["r3quality"],
            r4Quality=raw_data["r4quality"],
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

    def measurements(self, raw_data):
        return dict(
            date=raw_data["date"],
            ae=raw_data['ae'],
            ai=raw_data['ai'],
            bill=raw_data['bill'],
            dateDownload=raw_data['dateDownload'],
            dateUpdate=raw_data['dateUpdate'],
            r1=raw_data['r1'],
            r2=raw_data['r2'],
            r3=raw_data['r3'],
            r4=raw_data['r4'],
            season=raw_data['season'],
            source=raw_data['source'],
            validated=raw_data['validated'],
        )

class TgCchAutoconsRepository(MongoCurveRepository):
    model='tg_cch_autocons'

    def measurements(self, raw_data):
        return dict(
            date=raw_data["date"],
            ae=raw_data['ae'],
            ai=raw_data['ai'],
            bill=raw_data['bill'],
            dateDownload=raw_data['dateDownload'],
            dateUpdate=raw_data['dateUpdate'],
            r1=raw_data['r1'],
            r2=raw_data['r2'],
            r3=raw_data['r3'],
            r4=raw_data['r4'],
            season=raw_data['season'],
            source=raw_data['source'],
            validated=raw_data['validated'],
        )

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
