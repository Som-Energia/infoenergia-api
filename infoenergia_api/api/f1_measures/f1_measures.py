from datetime import datetime
from base64 import urlsafe_b64encode, urlsafe_b64decode

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.f1 import async_get_invoices
from infoenergia_api.contrib import Pagination
from infoenergia_api.utils import make_uuid

bp_f1_measures = Blueprint('f1')


class PaginationLinksMixin:

    async def _pagination_links(self, request, request_id, pagination_list, endpoint_name, **kwargs):

        url = request.url_for(endpoint_name, **kwargs)
        cursor_list = pagination_list.next_cursor
        next_cursor = urlsafe_b64encode(
            '{request_id}:{cursor}'.format(
                request_id=request_id,
                cursor=cursor_list
            ).encode()
        ).decode() if cursor_list else ''

        next_page = '{url}?cursor={cursor}&limit={limit}'.format(
            url=url,
            cursor=next_cursor,
            limit=pagination_list.page_size
        ) if next_cursor else False

        return dict(
            cursor=next_cursor,
            next_page=next_page
        )


class F1MeasuresContractIdView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, contractId):
        args = request.args
        page_size = int(args.get('limit', request.app.get('MAX_RESULT_SIZE', 50)))
        links = {}

        logger.info("Getting f1 measures for contract %s", contractId)

        if 'cursor' in args:
            request_id, cursor = urlsafe_b64decode(
                args.get('cursor').encode()
            ).decode().split(':')
            invoices_pagination = request.app.session[request_id]
            invoices = invoices_pagination.page(cursor)
            links = await self._pagination_links(
                request, request_id, invoices_pagination,  'f1.get_f1_measures_by_contract_id',
                contractId=contractId
            )
        else:
            invoices = await async_get_invoices(request, contractId)
            if len(invoices) > page_size:
                request_id = make_uuid(str(datetime.now()), id(request))
                invoices_pagination = Pagination(list(invoices), page_size)
                invoices = invoices_pagination.page(invoices_pagination.cursor)
                links = await self._pagination_links(
                    request, request_id, invoices_pagination, 'f1.get_f1_measures_by_contract_id',
                    contractId=contractId
                )
                request.app.session[request_id] = invoices_pagination

        f1_measure_json = [invoice.f1_measures for invoice in invoices]
        response = {
            'count': len(f1_measure_json),
            'data': f1_measure_json
        }
        response.update(links)
        return json(response)


class F1MeasuresView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request):
        args = request.args
        page_size = int(args.get('limit', request.app.get('MAX_RESULT_SIZE', 50)))
        links = {}
        logger.info(f"Getting f1 measures for {args}")
        if 'cursor' in args:
            request_id, cursor = urlsafe_b64decode(
                args.get('cursor').encode()
            ).decode().split(':')
            invoices_pagination = request.app.session[request_id]
            invoices = invoices_pagination.page(cursor)
            links = await self._pagination_links(
                request, request_id, invoices_pagination, 'f1.get_f1_measures'
            )
        else:
            invoices = await async_get_invoices(request)
            logger.info(f"There are {len(invoices)} invoices to process")
            if len(invoices) > page_size:
                request_id = make_uuid(str(datetime.now()), id(request))
                invoices_pagination = Pagination(list(invoices), page_size)
                invoices = invoices_pagination.page(invoices_pagination.cursor)
                links = await self._pagination_links(
                    request, request_id, invoices_pagination,'f1.get_f1_measures'
                )
                request.app.session[request_id] = invoices_pagination

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
