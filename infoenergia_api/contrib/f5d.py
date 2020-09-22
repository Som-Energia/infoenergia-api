import functools
import re
from datetime import datetime, timedelta
import pytz

from sanic.request import RequestParameters

from sanic.log import logger

from ..utils import (get_cch_filters, get_request_filters, make_uuid)


class F5D(object):

    def __init__(self, f5d_id):
        from infoenergia_api.app import app

        self._erp = app.erp_client
        self._mongo = app.mongo_client.somenergia
        self._F5D = self._mongo.tg_cchfact

        for name, value in self._F5D.find_one({"id": f5d_id}).items():
            setattr(self, name, value)


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

    @property
    def is_valid_empowering(self):
        contract_obj = self._erp.model('giscedata.polissa')

        filters = [
                ('active', '=', True),
                ('state', '=', 'activa'),
                ('empowering_profile_id', '=', 1),
                ('cups', '=', self.name)
            ]

        contract = contract_obj.search(filters)
        return bool(contract)

    @property
    def f5d_measures(self):
        if self.is_valid_empowering:
            return {
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

    if request.args:
        filters = get_request_filters(
            request.app.erp_client,
            request,
            filters,
        )
    contracts = contract_obj.search(filters)
    return [contract_obj.read(contract, ['cups'])['cups'][1] for contract in contracts]


def get_f5d(request, contractId=None):
    tg_cchfact = request.app.mongo_client.somenergia.tg_cchfact
    filters = {}

    if contractId:
        cups = get_cups(request, contractId)
        filters.update({"name": { "$in": cups }})

    if request.args:
        filters = get_cch_filters(request, filters)

    return [f5d['id'] for f5d in tg_cchfact.find(filters)]


async def async_get_f5d(request, id_contract=None):
    try:
        f5ds = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_f5d, request, id_contract)
        )
    except Exception as e:
        raise e
    return f5ds
