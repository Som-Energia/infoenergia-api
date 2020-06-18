from base64 import urlsafe_b64encode, urlsafe_b64decode

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.f1 import async_get_invoices, Invoice
from infoenergia_api.contrib import Pagination, PaginationLinksMixin

bp_f1_measures = Blueprint('f1')


class F1MeasuresContractIdView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        protected(),
    ]

    endpoint_name = 'f1.get_f1_measures_by_contract_id'

    async def get(self, request, contractId):
        logger.info("Getting f1 measures for contract: %s", contractId)
        invoices_ids, links = await self.paginate_results(
            request, function=async_get_invoices, contractId=contractId
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
        invoices_ids, links = await self.paginate_results(
            request,
            function=async_get_invoices
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
