import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.f1 import async_get_invoices

bp_f1_measures = Blueprint('f1')


class F1MeasuresContractIdView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, contractId):
        invoices = await async_get_invoices(request, contractId)
        f1_measure_json = [invoice.f1_measures for invoice in invoices]
        return json(f1_measure_json)


class F1MeasuresView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request):
        invoices = await async_get_invoices(request)
        f1_measure_json = [invoice.f1_measures for invoice in invoices]
        return json(f1_measure_json)


bp_f1_measures.add_route(
    F1MeasuresView.as_view(),
    '/f1/',
    name='get_f1_measures',
)

bp_f1_measures.add_route(
    F1MeasuresContractIdView.as_view(),
    '/f1/<contractId>',
    name='get_f1_measures_by_contract_id'
)
