import asyncio
from bson.objectid import ObjectId
from datetime import timedelta, datetime
import pytz

from sanic import Sanic
from somutils import isodates

from config import config

from ..utils import (
    get_cch_query, make_uuid, get_contract_id,
    iso_format, iso_format_tz, increment_isodate
)
from ..tasks import get_cups
from .erp import get_erp_instance

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
    async def search(cls, mongo_client, collection, filters, cups):
        query = await get_cch_query(filters, cups)
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
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, "tg_cchfact")
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
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, "tg_cchval")
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


class TgCchP1(BaseCch):
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, "tg_p1")
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


class BaseErpCch:

    _erp = get_erp_instance()
    timefield = 'datetime'

    @classmethod
    def to_filter(cls, filters):
        return [(cls.timefield, '<', increment_isodate(filters['to_'][0]))]

    @classmethod
    async def build_query(cls, filters):
        result = []
        if 'from_' in filters:
            result += [(cls.timefield, '>=', filters['from_'][0])]

        if 'to_' in filters:
            result += cls.to_filter(filters)

        if 'downloaded_from' in filters:
            result += [('create_at', '>=', filters['downloaded_from'][0])]

        if 'downloaded_to' in filters:
            result += [('create_at', '<=', filters['downloaded_to'][0])]

        if 'cups' in filters:
            # Not using ilike because ERP model turns it into
            # into '=' anyway, see the erp code
            result += [('name', '=', filters['cups'][0])]

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
    async def search(cls, erp, collection, filters, cups):
        loop = asyncio.get_running_loop()
        erp_model = erp.model(cls.erp_model_name)
        query = await cls.build_query(dict(filters, cups=cups))
        print(query)
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
        return [(cls.timefield, '<=', filters['to_'][0])]

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


async def async_get_cch(request, contract_id=None):
    loop = asyncio.get_running_loop()
    filters = request.args
    cups = None

    if contract_id:
        cups = await loop.run_in_executor(None, get_cups, request, contract_id)
        if not cups:
            return []

    collection = filters.get("type")
    model = cch_model(collection)
    if collection not in config.ERP_CURVES:
        return await model.search(
            request.app.ctx.mongo_client, collection, filters, cups
        )

    return await model.search(get_erp_instance(), collection, filters, cups)


def cch_model(type_name):
    return {
        "tg_cchfact": TgCchF5d,
        "tg_cchval": TgCchVal,
        "tg_f1": TgCchF1,
        "tg_gennetabeta": TgCchGennetabeta,
        "tg_cchautocons": TgCchAutocons,
        "P1": TgCchP1,
        "P2": TgCchP1,
    }.get(type_name, None)

