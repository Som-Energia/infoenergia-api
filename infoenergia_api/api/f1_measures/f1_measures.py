import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.request import RequestParameters
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.f1 import async_get_invoices
from infoenergia_api.contrib import Pagination

bp_f1_measures = Blueprint('f1')


class F1MeasuresContractIdView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, contractId):
        invoices, cursor, results = await async_get_invoices(request, contractId)
        f1_measure_json = [invoice.f1_measures for invoice in invoices]
        return json({
            'count': results,
            'links': cursor,
            'data': f1_measure_json
        })


class F1MeasuresView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def _pagination_links(self, request, pagination_list):
        next_cursor = pagination_list.next_cursor
        return dict(
            cursor=next_cursor,
            next_page='{url}?cursor={cursor}&limit={limit}'.format(
                url=request.url_for('f1.get_f1_measures'),
                cursor=next_cursor,
                limit=pagination_list.page_size
            )
        )


    async def get(self, request):
        args = RequestParameters(request.args)
        query_params = RequestParameters(request.args)
        page_size = int(query_params.get('limit', request.app.get('MAX_RESULT_SIZE', 50)))
        links = {}

        invoices = await async_get_invoices(request)
        if len(invoices) > page_size:
            invoices_pagination = Pagination(list(invoices), page_size)
            invoices = invoices_pagination.page(invoices_pagination.cursor)
            links = await self._pagination_links(request, invoices_pagination)

        f1_measure_json = [invoice.f1_measures for invoice in invoices]
        response = {
            'count': len(f1_measure_json),
            'data': f1_measure_json
        }
        response.update(links)

        return json(response)


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
