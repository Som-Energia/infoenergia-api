import asyncio
from datetime import datetime
from base64 import urlsafe_b64encode, urlsafe_b64decode

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.request import RequestParameters
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.f1 import async_get_invoices
from infoenergia_api.contrib import Pagination
from infoenergia_api.utils import make_uuid

bp_f1_measures = Blueprint('f1')


class F1MeasuresContractIdView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def _pagination_links(self, request, request_id, contract_id, pagination_list):
        next_cursor = urlsafe_b64encode(
            '{request_id}:{cursor}'.format(
                request_id=request_id,
                cursor=pagination_list.next_cursor
            ).encode()
        ).decode()

        return dict(
            cursor=next_cursor,
            next_page='{url}?cursor={cursor}&limit={limit}'.format(
                url=request.url_for(
                    'f1.get_f1_measures_by_contract_id', contractId=contract_id
                ),
                cursor=next_cursor,
                limit=pagination_list.page_size
            )
        )

    async def get(self, request, contractId):
        args = request.args
        page_size = int(args.get('limit', request.app.get('MAX_RESULT_SIZE', 50)))
        links = {}

        if 'cursor' in args:
            import pdb; pdb.set_trace()
            request_id, cursor = urlsafe_b64decode(
                args.get('cursor').encode()
            ).decode().split(':')
            invoices_pagination = request['session'][request_id]
            invoices = invoices_pagination.page(cursor)
            links = await self._pagination_links(
                request, request_id, contractId, invoices_pagination
            )
        else:
            invoices = await async_get_invoices(request, contractId)
            if len(invoices) > page_size:
                request_id = make_uuid(str(datetime.now()), id(request))
                invoices_pagination = Pagination(list(invoices), page_size)
                invoices = invoices_pagination.page(invoices_pagination.cursor)
                links = await self._pagination_links(
                    request, request_id, contractId, invoices_pagination
                )
                request['session'][request_id] = invoices_pagination

        f1_measure_json = [invoice.f1_measures for invoice in invoices]
        response = {
            'count': len(f1_measure_json),
            'data': f1_measure_json
        }
        response.update(links)
        return json(response)

class F1MeasuresView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def _pagination_links(self, request, request_id, pagination_list):
        next_cursor = urlsafe_b64encode(
            '{request_id}:{cursor}'.format(
                request_id=request_id,
                cursor=pagination_list.next_cursor
            ).encode()
        ).decode()

        return dict(
            cursor=next_cursor,
            next_page='{url}?cursor={cursor}&limit={limit}'.format(
                url=request.url_for('f1.get_f1_measures'),
                cursor=next_cursor,
                limit=pagination_list.page_size
            )
        )


    async def get(self, request):
        args = request.args
        page_size = int(args.get('limit', request.app.get('MAX_RESULT_SIZE', 50)))
        links = {}

        if 'cursor' in args:
            request_id, cursor = urlsafe_b64decode(args['cursor']).split(':')
            invoices_pagination = request['session'][request_id]
            invoices = invoices_pagination.page(cursor)
            links = await self._pagination_links(request, request_id, invoices_pagination)
        else:
            invoices = await async_get_invoices(request)
            if len(invoices) > page_size:
                request_id = make_uuid(str(datetime.now()), id(request))
                invoices_pagination = Pagination(list(invoices), page_size)
                invoices = invoices_pagination.page(invoices_pagination.cursor)
                links = await self._pagination_links(request, request_id, invoices_pagination)
                request['session'][request_id] = invoices_pagination

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
