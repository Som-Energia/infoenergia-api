from bson.objectid import ObjectId
from datetime import timedelta
import pytz

from ..utils import (
    get_cch_filters, make_uuid, get_contract_id
)
from ..tasks import get_cups


class Cch(object):

    @classmethod
    async def create(cls, cch_id, collection):
        from infoenergia_api.app import app

        self = cls()
        self._erp = app.erp_client
        self._executor = app.thread_pool
        self._mongo = app.mongo_client.somenergia
        self._collection = collection
        self._Cch = self._mongo[self._collection]
        curve = await self._Cch.find_one({"_id": ObjectId(str(cch_id))})
        for name, value in curve.items():
            setattr(self, name, value)
        return self

    @property
    def dateCch(self):
        tz = pytz.timezone('Europe/Madrid')

        date_cch = tz.localize(
            self.datetime,
            is_dst=self.season).astimezone(pytz.utc)
        date_cch -= timedelta(hours=1)
        return date_cch.strftime("%Y-%m-%d %H:%M:%S%z")

    @property
    def measurements(self):
        if self._collection == 'tg_cchfact':
            return {
                'season': self.season,
                'ai': self.ai,
                'ao': self.ao,
                'r1': self.r1,
                'r2': self.r2,
                'r3': self.r3,
                'r4': self.r4,
                'source': self.source,
                'validated': self.validated,
                'date': self.dateCch,
                'dateDownload': (self.create_at).strftime("%Y-%m-%d %H:%M:%S"),
                'dateUpdate': (self.update_at).strftime("%Y-%m-%d %H:%M:%S")
            }
        if self._collection == 'tg_cchval':
            return {
                'season': self.season,
                'ai': self.ai,
                'ao': self.ao,
                'date': self.dateCch,
                'dateDownload': (self.create_at).strftime("%Y-%m-%d %H:%M:%S"),
                'dateUpdate': (self.update_at).strftime("%Y-%m-%d %H:%M:%S")
            }
        if self._collection == 'tg_f1':
            return {
                'season': self.season,
                'ai': self.ai,
                'ao': self.ao,
                'r1': self.r1,
                'r2': self.r2,
                'r3': self.r3,
                'r4': self.r4,
                'source': self.source,
                'validated': self.validated,
                'date': self.dateCch,
                'dateDownload': (self.create_at).strftime("%Y-%m-%d %H:%M:%S"),
                'dateUpdate': (self.update_at).strftime("%Y-%m-%d %H:%M:%S"),
                'reserve1': self.reserve1,
                'reserve2': self.reserve2,
                'measureType': self.measure_type,
            }
        if self._collection == 'tg_p1':
            return {
                'date': self.dateCch,
                'season': self.season,
                'ai': self.ai,
                'aiquality': self.aiquality,
                'ao': self.ao,
                'aoQuality': self.aoquality,
                'source': self.source,
                'validated': self.validated,
                'type': self.type,
                'reserve1': self.reserve1,
                'reserve1Quality': self.reserve1quality,
                'reserve2': self.reserve2,
                'reserve2Quality': self.reserve2quality,
                'r4': self.r4,
                'r4Quality': self.r4quality,
                'r2': self.r2,
                'r2Quality': self.r2quality,
                'r3': self.r3,
                'r3Quality': self.r3quality,
                'r1': self.r1,
                'r1Quality': self.r1quality,
                'measureType': self.measure_type,
                'dateDownload': (self.create_at).strftime("%Y-%m-%d %H:%M:%S"),
                'dateUpdate': (self.update_at).strftime("%Y-%m-%d %H:%M:%S"),
            }

    async def cch_measures(self, user, request, contractId=None):
        if contractId:
            return {
                'contractId': contractId,
                'meteringPointId': make_uuid('giscedata.cups.ps', self.name),
                'measurements': self.measurements
            }
        else:
            contractId = await request.app.loop.run_in_executor(
                self._executor,
                get_contract_id,
                self._erp,
                self.name,
                user,
            )
            if contractId:
                return {
                    'contractId': contractId,
                    'meteringPointId': make_uuid('giscedata.cups.ps', self.name),
                    'measurements': self.measurements
                }
            return {}


async def async_get_cch(request, contractId=None):
    collection = str(request.args['type'][0])
    if collection in ('P1', 'P2'):
        collection = 'tg_p1'
    cch_collection = request.app.mongo_client.somenergia[collection]
    filters = {}

    if contractId:
        cups = await request.app.loop.run_in_executor(
            request.app.thread_pool, get_cups, request, contractId
        )
        if not cups:
            return []
        filters.update({"name": {'$regex': '^{}'.format(cups[0][:20])}})

    if request.args:
        filters = await get_cch_filters(request, filters)
   
    return [
        cch['_id']
        async for cch in cch_collection.find(filters)
        if cch.get('_id')
    ]
