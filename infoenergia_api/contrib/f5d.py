from bson.objectid import ObjectId
from datetime import timedelta
import pytz

from ..utils import (
    get_cch_filters, get_request_filters, make_uuid, get_contract_user_filters
)


class F5D(object):

    @classmethod
    async def create(cls, f5d_id):
        from infoenergia_api.app import app
        self = cls()
        self._erp = app.erp_client
        self._mongo = app.mongo_client.somenergia
        self._F5D = self._mongo.tg_cchfact
        curve = await self._F5D.find_one({"_id": ObjectId(str(f5d_id))})
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
        return {
                'season': self.season,
                'r1': self.r1,
                'r2': self.r2,
                'r3': self.r3,
                'r4': self.r4,
                'ai': self.ai,
                'ao': self.ao,
                'source': self.source,
                'validated': self.validated,
                'date': self.dateCch,
                'dateDownload': (self.create_at).strftime("%Y-%m-%d %H:%M:%S"),
                'dateUpdate': (self.update_at).strftime("%Y-%m-%d %H:%M:%S")
        }


    def is_valid_contract(self, user):
        contract_obj = self._erp.model('giscedata.polissa')

        filters = [
                ('active', '=', True),
                ('state', '=', 'activa'),
                ('empowering_profile_id', '=', 1),
                ('cups', 'ilike', self.name)
            ]
        filters = get_contract_user_filters(self._erp, user, filters)
        contract = contract_obj.search(filters)
        if contract:
            return contract_obj.read(contract, ['name'])[0]['name']

    def f5d_measures(self, user):
        if self.is_valid_contract(user):
            return {
            'contractId': self.is_valid_contract(user),
            'meteringPointId': make_uuid('giscedata.cups.ps', self.name),
            'measurements': self.measurements
            }


def get_cups(request, contractId=None):
    contract_obj = request.app.erp_client.model('giscedata.polissa')
    filters = [
        ('active', '=', True),
        ('state', '=', 'activa'),
        ('empowering_profile_id', '=', 1),
        ('name', '=', contractId)
    ]

    filters = get_contract_user_filters(
        request.app.erp_client, request.ctx.user, filters
    )

    if request.args:
        filters = get_request_filters(
            request.app.erp_client,
            request,
            filters,
        )
    contracts = contract_obj.search(filters)
    return [contract_obj.read(contract, ['cups'])['cups'][1] for contract in contracts]


async def async_get_f5d(request, contractId=None):
    tg_cchfact = request.app.mongo_client.somenergia.tg_cchfact
    filters = {}

    if contractId:
        cups = get_cups(request, contractId)
        if not cups:
            return []
        filters.update({"name": {'$regex': '^{}'.format(cups[0][:20])}})

    if request.args:
        filters = get_cch_filters(request, filters)

    return [f5d['_id'] async for f5d in tg_cchfact.find(filters) if f5d.get('_id')]
