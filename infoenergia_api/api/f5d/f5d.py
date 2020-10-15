from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import inject_user, protected

from infoenergia_api.contrib.f5d import async_get_f5d, F5D
from infoenergia_api.contrib import PaginationLinksMixin

bp_f5d_measures = Blueprint('f5d')


class F5DMeasuresContractIdView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'f5d.get_f5d_measures_by_contract_id'

    async def get(self, request, contractId, user):
        logger.info("Getting f5d measures for contract: %s", contractId)
        request.ctx.user = user

        f5d_ids, links = await self.paginate_results(
            request,
            function=async_get_f5d, contractId=contractId
        )

        f5d_measure_json = [
            (await F5D.create(f5d_id)).f5d_measures(user) for f5d_id in f5d_ids
        ]

        response = {
            'count': len(f5d_measure_json),
            'data': f5d_measure_json
        }
        response.update(links)
        return json(response)


class F5DMeasuresView(PaginationLinksMixin, HTTPMethodView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'f5d.get_f5d_measures'

    async def get(self, request, user):
        request.ctx.user = user
        logger.info("Getting f5d measures")
        f5d_ids, links = await self.paginate_results(
            request,
            function=async_get_f5d
        )

        f5d_measure_json = [
            (await F5D.create(f5d_id)).f5d_measures(user) for f5d_id in f5d_ids
        ]

        response = {
            'count': len(f5d_measure_json),
            'data': f5d_measure_json
        }
        response.update(links)
        return json(response)


bp_f5d_measures.add_route(
    F5DMeasuresView.as_view(),
    '/f5d/',
    name='get_f5d_measures',
)

bp_f5d_measures.add_route(
    F5DMeasuresContractIdView.as_view(),
    '/f5d/<contractId>',
    name='get_f5d_measures_by_contract_id'
)
