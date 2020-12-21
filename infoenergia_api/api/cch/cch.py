from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import inject_user, protected

from infoenergia_api.contrib.cch import async_get_cch, Cch
from infoenergia_api.contrib import PaginationLinksMixin

bp_cch_measures = Blueprint('cch')


class CchMeasuresContractIdView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'cch.get_cch_measures_by_contract_id'

    async def get(self, request, contractId, user):
        logger.info("Getting cch measures for contract: %s", contractId)
        request.ctx.user = user

        cch_ids, links, total_results = await self.paginate_results(
            request,
            function=async_get_cch, contractId=contractId
        )
        collection = request.args['type'][0]
        cch_measure_json = [
            (await Cch.create(cch_id, collection)).cch_measures(user) for cch_id in cch_ids
        ]

        response = {
            'total_results': total_results,
            'count': len(cch_measure_json),
            'data': cch_measure_json
        }
        response.update(links)
        return json(response)


class CchMeasuresView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'cch.get_cch_measures'

    async def get(self, request, user):
        request.ctx.user = user
        logger.info("Getting cch measures")
        cch_ids, links, total_results = await self.paginate_results(
            request,
            function=async_get_cch
        )

        collection = request.args['type'][0]
        cch_measure_json = [
            (await Cch.create(cch_id, collection)).cch_measures(user) for cch_id in cch_ids
        ]

        response = {
            'total_results': total_results,
            'count': len(cch_measure_json),
            'data': cch_measure_json
        }
        response.update(links)
        return json(response)


bp_cch_measures.add_route(
    CchMeasuresView.as_view(),
    '/cch/',
    name='get_cch_measures',
)

bp_cch_measures.add_route(
    CchMeasuresContractIdView.as_view(),
    '/cch/<contractId>',
    name='get_cch_measures_by_contract_id'
)
