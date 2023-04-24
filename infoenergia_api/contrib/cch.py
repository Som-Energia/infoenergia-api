import asyncio
from bson.objectid import ObjectId
from datetime import timedelta, datetime
import pytz

from sanic import Sanic
from somutils import isodates

from config import config

from ..utils import (
    make_uuid, get_contract_id,
    iso_format, iso_format_tz,
    increment_isodate,
    isodate2datetime,
)
from ..tasks import get_cups
from .erp import get_erp_instance
from .mongo_manager import get_mongo_instance

class BaseCch:

    _erp = get_erp_instance()

    @classmethod
    async def create(cls, cch_id, collection):
        app = Sanic.get_app()
        self = cls()
        self._executor = app.ctx.thread_pool
        self._mongo = app.ctx.mongo_client.somenergia
        self._collection = collection
        self._Cch = self._mongo[self._collection]
        self.raw_curve = await self._Cch.find_one({"_id": ObjectId(str(cch_id))}) or {}
        for name, value in self.raw_curve.items():
            setattr(self, name, value)
        return self

    @classmethod
    async def build_query(cls, filters):
        query = {}
        if "from_" in filters:
            query.setdefault('datetime', {}).update(
                {"$gte": isodate2datetime(filters["from_"])}
            )

        if "to_" in filters:
            query.setdefault('datetime', {}).update(
                {"$lte": isodate2datetime(increment_isodate(filters["to_"]))}
            )

        if "downloaded_from" in filters:
            query.setdefault('create_at', {}).update(
                {"$gte": isodate2datetime(filters["downloaded_from"])}
            )

        if "downloaded_to" in filters:
            query.setdefault('create_at', {}).update(
                {"$lte": isodate2datetime(filters["downloaded_to"])}
            )

        if "P1" in filters["type"].upper():
            query.update({"type": {"$eq": "p"}})

        if "P2" in filters["type"].upper():
            query.update({"type": {"$eq": "p4"}})

        if filters.get("cups",None):
            query.update(name={"$regex": "^{}".format(filters["cups"][:20])})

        return query

    @classmethod
    async def search(cls, collection, filters, cups):
        app = Sanic.get_app()
        mongo_client = app.ctx.mongo_client
        query = await cls.build_query(dict(filters, cups=cups))
        if collection in ("P1", "P2"):
            collection = "tg_p1"
        cch_collection = mongo_client.somenergia[collection]

        return [cch["_id"] async for cch in cch_collection.find(query) if cch.get("_id")]

    @property
    def date_cch(self):
        if not self.raw_curve:
            return

        tz = pytz.timezone("Europe/Madrid")

        date_cch = tz.localize(self.datetime, is_dst=self.season).astimezone(pytz.utc)
        date_cch -= timedelta(hours=1)
        return iso_format_tz(date_cch)

    async def cch_measures(self, user, contract_id=None):
        loop = asyncio.get_running_loop()
        if not self.raw_curve:
            return {}

        if not contract_id:
            contract_id = await loop.run_in_executor(
                None,
                get_contract_id,
                self._erp,
                self.name,
                user,
            )
        if contract_id:
            return {
                "contractId": contract_id,
                "meteringPointId": make_uuid("giscedata.cups.ps", self.name),
                "measurements": self.measurements,
            }

        return {}


class TgCchF5d(BaseCch):
    mongo_collection = "tg_cchfact"
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, cls.mongo_collection)
        return cch_fact_curve

    @property
    def measurements(self):
        if not self.raw_curve:
            return {}

        return {
            "season": self.season,
            "ai": self.ai,
            "ao": self.ao,
            "r1": self.r1,
            "r2": self.r2,
            "r3": self.r3,
            "r4": self.r4,
            "source": self.source,
            "validated": self.validated,
            "date": self.date_cch,
            "dateDownload": iso_format(self.create_at),
            "dateUpdate": iso_format(self.update_at),
        }


class TgCchVal(BaseCch):
    mongo_collection = "tg_cchval"
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, cls.mongo_collection)
        return cch_fact_curve

    @property
    def measurements(self):
        if not self.raw_curve:
            return {}

        return {
            "season": self.season,
            "ai": self.ai,
            "ao": self.ao,
            "date": self.date_cch,
            "dateDownload": iso_format(self.create_at),
            "dateUpdate": iso_format(self.update_at),
        }

class TgCchPn(BaseCch):
    mongo_collection = "tg_p1"
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, cls.mongo_collection)
        return cch_fact_curve

    @property
    def measurements(self):
        if not self.raw_curve:
            return {}

        return {
            "date": self.date_cch,
            "season": self.season,
            "ai": self.ai,
            "aiquality": self.aiquality,
            "ao": self.ao,
            "aoQuality": self.aoquality,
            "source": self.source,
            "validated": self.validated,
            "type": self.type,
            "reserve1": self.reserve1,
            "reserve1Quality": self.reserve1quality,
            "reserve2": self.reserve2,
            "reserve2Quality": self.reserve2quality,
            "r4": self.r4,
            "r4Quality": self.r4quality,
            "r2": self.r2,
            "r2Quality": self.r2quality,
            "r3": self.r3,
            "r3Quality": self.r3quality,
            "r1": self.r1,
            "r1Quality": self.r1quality,
            "measureType": self.measure_type,
            "dateDownload": iso_format(self.create_at),
            "dateUpdate": iso_format(self.update_at),
        }

class TgCchP1(TgCchPn):
    @classmethod
    async def build_query(cls, filters):
        query = await super().build_query(filters)
        query.update({"type": {"$eq": "p"}})
        return query

class TgCchP2(TgCchPn):
    @classmethod
    async def build_query(cls, filters):
        query = await super().build_query(filters)
        query.update({"type": {"$eq": "p4"}})
        return query

class BaseErpCch:

    _erp = get_erp_instance()
    timefield = 'datetime'

    @classmethod
    def to_filter(cls, filters):
        return [(cls.timefield, '<', increment_isodate(filters['to_']))]

    @classmethod
    async def build_query(cls, filters):
        result = []
        if 'from_' in filters:
            result += [(cls.timefield, '>=', filters['from_'])]

        if 'to_' in filters:
            result += cls.to_filter(filters)

        if 'downloaded_from' in filters:
            result += [('create_at', '>=', filters['downloaded_from'])]

        if 'downloaded_to' in filters:
            result += [('create_at', '<=', filters['downloaded_to'])]

        if 'cups' in filters:
            # Not using ilike because ERP model turns it into
            # into '=' anyway, see the erp code
            result += [('name', '=', filters['cups'])]

        return result

    @classmethod
    async def create(cls, cch_id):
        if not hasattr(cls, 'erp_model'):
            cls.erp_model = cls._erp.model(cls.erp_model_name)
        self = cls()
        self._loop = asyncio.get_running_loop()
        self.raw_curve = await self._loop.run_in_executor(
            None, self.erp_model.read, cch_id
        )
        for name, value in self.raw_curve.items():
            setattr(self, name, value)
        return self

    @classmethod
    async def search(cls, collection, filters, cups):
        loop = asyncio.get_running_loop()
        erp_model = cls._erp.model(cls.erp_model_name)
        query = await cls.build_query(dict(filters, cups=cups))
        return await loop.run_in_executor(None, erp_model.search, query)

    async def cch_measures(self, user, contract_id=None):
        loop = asyncio.get_running_loop()
        if not self.raw_curve:
            return {}

        if not contract_id:
            contract_id = await loop.run_in_executor(
                None,
                get_contract_id,
                self._erp,
                self.name,
                user,
            )
        if contract_id:
            return {
                "contractId": contract_id,
                "meteringPointId": make_uuid("giscedata.cups.ps", self.name),
                "measurements": self.measurements,
            }

        return {}

class BaseTimescaleErpCch(BaseErpCch):
    timefield = 'utc_timestamp'

    @classmethod
    def to_filter(cls, filters):
        return [(cls.timefield, '<=', filters['to_'])]

class TgCchF1(BaseTimescaleErpCch):

    erp_model_name = "tg.f1"

    @property
    def date_cch(self):
        _utc_timestamp = datetime.strptime(
            self.utc_timestamp, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=pytz.UTC)
        return iso_format_tz(_utc_timestamp)

    @property
    def measurements(self):
        if not self.raw_curve:
            return {}

        return {
            "season": self.season,
            "ai": self.ai,
            "ao": self.ao,
            "r1": self.r1,
            "r2": self.r2,
            "r3": self.r3,
            "r4": self.r4,
            "source": self.source,
            "validated": self.validated,
            "date": self.date_cch,
            "dateDownload": self.create_at,
            "dateUpdate": self.update_at,
            "reserve1": self.reserve1,
            "reserve2": self.reserve2,
            "measureType": self.measure_type,
        }


class TgCchGennetabeta(BaseErpCch):

    erp_model_name = "tg.cch_gennetabeta"
    timefield = 'datetime'

    @property
    def date_cch(self):
        localtime = isodates.parseLocalTime(self.datetime, isSummer=self.season)
        return iso_format_tz(localtime)

    @property
    def measurements(self):
        if not self.raw_curve:
            return {}

        return {
            "ae": self.ae,
            "ai": self.ai,
            "bill": self.bill,
            "dateDownload": self.create_at,
            "dateUpdate": self.update_at,
            "date": self.date_cch,
            "r1": self.r1,
            "r2": self.r2,
            "r3": self.r3,
            "r4": self.r4,
            "season": self.season,
            "source": self.source,
            "validated": self.validated,
        }


class TgCchAutocons(BaseErpCch):

    erp_model_name = "tg.cch_autocons"

    @property
    def date_cch(self):
        localtime = isodates.parseLocalTime(self.datetime, isSummer=self.season)
        return iso_format_tz(localtime)

    @property
    def measurements(self):
        if not self.raw_curve:
            return {}

        return {
            "ae": self.ae,
            "ai": self.ai,
            "bill": self.bill,
            "dateDownload": self.create_at,
            "dateUpdate": self.update_at,
            "date": self.date_cch,
            "r1": self.r1,
            "r2": self.r2,
            "r3": self.r3,
            "r4": self.r4,
            "season": self.season,
            "source": self.source,
            "validated": self.validated,
        }


# New implementations

class MongoCurveRepository():
    extra_filter = dict()

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
                {"$gte": isodate2datetime(start)}
            )
        if end:
            query.setdefault('datetime', {}).update(
                {"$lte": isodate2datetime(increment_isodate(end))}
            )
        if downloaded_from:
            query.setdefault('create_at', {}).update(
                {"$gte": isodate2datetime(downloaded_from)}
            )
        if downloaded_to:
            query.setdefault('create_at', {}).update(
                {"$lte": isodate2datetime(downloaded_to)}
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
            date_cch -= timedelta(hours=1)
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

class ErpMongoCurveRepository:

    extra_filter=dict()

    def __init__(self):
        self._erp = get_erp_instance()

    def to_filter(self, end):
        return [('datetime', '<', increment_isodate(end))]

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
            localtime = isodates.parseLocalTime(cch['datetime'], isSummer=cch['season'])
            return iso_format_tz(localtime)

        def cch_transform(cch):
            return dict(cch,
                date=erp_cch_tz_isodate(cch),
            )

        return [
            cch_transform(cch) for cch in cchs
        ]

class TimescaleCurveRepository:

    extra_filter=dict()

    def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        downloaded_from=None,
        downloaded_to=None,
        **extra_filter
    ):
        from .erpdb_manager import get_erpdb_instance
        from psycopg import AsyncClientCursor
        erpdb = await get_erpdb_instance()
        async with AsyncClientCursor(erpdb) as cursor:
            result = []
            if cups:
                # Not using ilike because ERP model turns it into
                # into '=' anyway, see the erp code
                result += [cursor.mogrify("name ILIKE %s", [cups[:20]+"%"])]

        return result
        result = []
        if cups:
            # Not using ilike because ERP model turns it into
            # into '=' anyway, see the erp code
            result += [f"name ILIKE '{cups[:20]}%'"]

        return result


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
    #"tg_f1": TgCchF1Repository,
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
    if curve_type in migrated_repositories:
        result = await get_curve(
            curve_type,
            start = filters.get('from_', None),
            end = filters.get('to_', None),
            cups = cups,
        )
        return result
    Cch = cch_model(curve_type)
    return await Cch.search(curve_type, filters, cups)


def cch_model(type_name):
    return {
        "tg_cchfact": TgCchF5d,
        "tg_cchval": TgCchVal,
        "tg_f1": TgCchF1,
        "tg_gennetabeta": TgCchGennetabeta,
        "tg_cchautocons": TgCchAutocons,
        "P1": TgCchP1,
        "P2": TgCchP2,
    }.get(type_name, None)

