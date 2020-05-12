import pickle
from datetime import datetime
from base64 import urlsafe_b64encode, urlsafe_b64decode

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.f1 import async_get_invoices, Invoice
from infoenergia_api.contrib import Pagination
from infoenergia_api.utils import make_uuid

bp_f1_measures = Blueprint('f1')


class PaginationLinksMixin:

    async def _pagination_links(self, request, request_id, pagination_list, **kwargs):

        url = request.url_for(self.endpoint_name, **kwargs)
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

    async def paginate_invoices(self, request, **kwargs):
        args = request.args
        page_size = int(args.get('limit', request.app.config.get('MAX_RESULT_SIZE', 50)))
        links = {}

        if 'cursor' in args:
            request_id, cursor = urlsafe_b64decode(
                args.get('cursor').encode()
            ).decode().split(':')
            invoices_pagination = pickle.loads(
                await request.app.redis.get(request_id)
            )
            invoices_ids = invoices_pagination.page(cursor)
            links = await self._pagination_links(
                request, request_id, invoices_pagination, **kwargs
            )
        else:
            contract_id = kwargs.get('contractId')
            invoices_ids = await async_get_invoices(request, contract_id)
            logger.info(f"There are {len(invoices_ids)} invoices to process")

            if len(invoices_ids) > page_size:
                request_id = make_uuid(str(datetime.now()), id(request))
                invoices_pagination = Pagination(invoices_ids, page_size)
                invoices_ids = invoices_pagination.page(invoices_pagination.cursor)
                links = await self._pagination_links(
                    request, request_id, invoices_pagination, **kwargs
                )
                await request.app.redis.set(
                    request_id, pickle.dumps(invoices_pagination)
                )
                await request.app.redis.expire(request_id, 3600 * 6)

        return invoices_ids, links


class F1MeasuresContractIdView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        protected(),
    ]

    endpoint_name = 'f1.get_f1_measures_by_contract_id'

    async def get(self, request, contractId):
        logger.info("Getting f1 measures for contract: %s", contractId)
        invoices_ids, links = await self.paginate_invoices(
            request, contractId=contractId
        )

        f1_measure_json = [
            await request.app.loop.run_in_executor(
                request.app.thread_pool, lambda: Invoice(invoice_id).f1_measures
            ) for invoice_id in invoices_ids
        ]

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

    endpoint_name = 'f1.get_f1_measures'

    async def get(self, request):
        logger.info("Getting f1 measures")
        invoices_ids, links = await self.paginate_invoices(request)

        f1_measure_json = [
            await request.app.loop.run_in_executor(
                request.app.thread_pool, lambda: Invoice(invoice_id).f1_measures
            ) for invoice_id in invoices_ids
        ]

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
