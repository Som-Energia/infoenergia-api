import asyncio
from bson.objectid import ObjectId
from datetime import timedelta
import pytz

from ..utils import get_cch_filters, make_uuid, get_contract_id
from ..tasks import get_cups


class BaseCch(object):

    iso_format = "%Y-%m-%d %H:%M:%S"

    @classmethod
    async def create(cls, cch_id, collection):
        from infoenergia_api.app import app

        self = cls()
        self._erp = app.ctx.erp_client
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
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, "tg_f1")
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
            "date": self.dateCch,
            "dateDownload": (self.create_at).strftime(self.iso_format),
            "dateUpdate": (self.update_at).strftime(self.iso_format),
            "reserve1": self.reserve1,
            "reserve2": self.reserve2,
            "measureType": self.measure_type,
        }


class TgCchP1(BaseCch):
    @classmethod
    async def create(cls, cch_id):
        cch_fact_curve = await super().create(cch_id, "tg_cchval")
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


async def async_get_cch(request, contract_id=None):
    filters = {}
    loop = asyncio.get_running_loop()

    collection = request.args.get("type")
    if collection in ("P1", "P2"):
        collection = "tg_p1"
    cch_collection = request.app.ctx.mongo_client.somenergia[collection]

    if contract_id:
        cups = await loop.run_in_executor(None, get_cups, request, contract_id)
        if not cups:
            return []
        filters.update({"name": {"$regex": "^{}".format(cups[0][:20])}})

    if request.args:
        filters = await get_cch_filters(request, filters)

    return [cch["_id"] async for cch in cch_collection.find(filters) if cch.get("_id")]
