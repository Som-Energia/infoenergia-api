import asyncio
from bson.objectid import ObjectId
from datetime import timedelta, datetime
import pytz

from sanic import Sanic
from somenergia_utils import isodates

from config import config

from ..utils import get_cch_query, make_uuid, get_contract_id, get_cch_erp_query
from ..tasks import get_cups
from .erp import get_erp_instance


class BaseCch(object):

    iso_format = "%Y-%m-%d %H:%M:%S"
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

    @property
    def date_cch(self):
        if not self.raw_curve:
            return

        tz = pytz.timezone("Europe/Madrid")

        date_cch = tz.localize(self.datetime, is_dst=self.season).astimezone(pytz.utc)
        date_cch -= timedelta(hours=1)
        return date_cch.strftime("%Y-%m-%d %H:%M:%S%z")

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
            "dateDownload": (self.create_at).strftime(self.iso_format),
            "dateUpdate": (self.update_at).strftime(self.iso_format),
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
            "dateDownload": (self.create_at).strftime(self.iso_format),
            "dateUpdate": (self.update_at).strftime(self.iso_format),
        }


class TgCchF1(BaseCch):

    erp_model = "tg.f1"

    @classmethod
    async def create(cls, cch_id):
        self = cls()
        self._loop = asyncio.get_running_loop()
        self.TgF1 = self._erp.model(self.erp_model)
        self.raw_curve = await self._loop.run_in_executor(None, self.TgF1.read, cch_id)

        for name, value in self.raw_curve.items():
            setattr(self, name, value)
        return self

    @property
    def date_cch(self):
        _utc_timestamp = datetime.strptime(
            self.utc_timestamp, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=pytz.UTC)
        return _utc_timestamp.strftime("%Y-%m-%d %H:%M:%S%z")

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
            "dateDownload": (self.create_at).strftime(self.iso_format),
            "dateUpdate": (self.update_at).strftime(self.iso_format),
        }


class TgCchGennetabeta(BaseCch):

    erp_model_name = "tg.cch_gennetabeta"

    @classmethod
    async def create(cls, cch_id):
        self = cls()
        self._loop = asyncio.get_running_loop()
        self.erp_model = self._erp.model(self.erp_model_name)
        self.raw_curve = await self._loop.run_in_executor(
            None, self.er_model.read, cch_id
        )

        for name, value in self.raw_curve.items():
            setattr(self, name, value)
        return self

    @property
    def date_cch(self):
        localtime = isodates.parseLocalTime(self.datetime, isSummer=self.season)
        return localtime.strftime("%Y-%m-%d %H:%M:%S%z")

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


class TgCchAutocons(BaseCch):
    erp_model_name = "tg.cch_autocons"

    @classmethod
    async def create(cls, cch_id):
        self = cls()
        self._loop = asyncio.get_running_loop()
        self.erp_model = self._erp.model(self.erp_model_name)
        self.raw_curve = await self._loop.run_in_executor(
            None, self.er_model.read, cch_id
        )

        for name, value in self.raw_curve.items():
            setattr(self, name, value)
        return self

    @property
    def date_cch(self):
        localtime = isodates.parseLocalTime(self.datetime, isSummer=self.season)
        return localtime.strftime("%Y-%m-%d %H:%M:%S%z")

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
    if collection not in config.ERP_CURVES:
        return await get_from_mongo(
            request.app.ctx.mongo_client, collection, filters, cups
        )

    return await get_from_erp(get_erp_instance(), collection, filters, cups)


async def get_from_mongo(mongo_client, collection, filters, cups):
    query = await get_cch_query(filters, cups)
    if collection in ("P1", "P2"):
        collection = "tg_p1"
    cch_collection = mongo_client.somenergia[collection]

    return [cch["_id"] async for cch in cch_collection.find(query) if cch.get("_id")]


async def get_from_erp(erp, collection, filters, cups):
    loop = asyncio.get_running_loop()
    collection_map = {
        "tg_f1": "tg.f1",
        "tg_gennetabeta": "tg.cch_gennetabeta",
        "tg_cchautocons": "tg.cch_autocons",
    }
    model = erp.model(collection_map.get(collection))
    query = await get_cch_erp_query(filters, cups)
    return await loop.run_in_executor(None, model.search, query)
