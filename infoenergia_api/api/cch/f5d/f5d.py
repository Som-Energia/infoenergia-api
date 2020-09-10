from base64 import urlsafe_b64encode, urlsafe_b64decode

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.f1 import async_get_invoices, Invoice
from infoenergia_api.contrib import Pagination, PaginationLinksMixin

bp_f5d_measures = Blueprint('f5d')


class F5DMeasuresContractIdView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        protected(),
    ]

    endpoint_name = 'f5d.get_f5d_measures_by_contract_id'

    async def get(self, request, contractId):
        logger.info("Getting f5d measures for contract: %s", contractId)
        f5d_ids, links = await self.paginate_results(
            request,
            function=async_get_f5d, contractId=contractId
        )

        f5d_measure_json = [
            await request.app.loop.run_in_executor(
                request.app.thread_pool, lambda: F5D(f5d_id).f5d_measures
            ) for f5d_id in f5d_ids
        ]


        response = {
            'count': len(f5d_measure_json),
            'data': f5d_measure_json
        }
        response.update(links)
        return json(response)


class F5DMeasuresView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        protected(),
    ]

    endpoint_name = 'f5d.get_f5d_measures'

    async def get(self, request):
        logger.info("Getting f5d measures")
        f5d_ids, links = await self.paginate_results(
            request,
            function=async_get_f5d
        )

        f5d_measure_json = [
            await request.app.loop.run_in_executor(
                request.app.thread_pool, lambda: F5D(f5d_id).f5d_measures
            ) for f5d_id in f5d_ids
        ]

        response = {
            'count': len(f5d_measure_json),
            'data': f5d_measure_json
        }
        response.update(links)
        return json(response)


bp_f1_measures.add_route(
    F1MeasuresView.as_view(),
    '/f5d/',
    name='get_f5d_measures',
)

bp_f1_measures.add_route(
    F1MeasuresContractIdView.as_view(),
    '/f5d/<contractId>',
    name='get_f5d_measures_by_contract_id'
)
