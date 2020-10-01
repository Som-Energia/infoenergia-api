from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected, inject_user

from infoenergia_api.contrib.contracts import Contract
from infoenergia_api.contrib.modcontracts import async_get_modcontracts
from infoenergia_api.contrib import PaginationLinksMixin


bp_modcontracts = Blueprint('modcontracts')


class ModContractsView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'modcontracts.get_modcontracts'

    async def get(self, request, user):
        logger.info("Getting contractual modifications")
        request.ctx.user = user
        contracts_ids, links = await self.paginate_results(
            request,
            function=async_get_modcontracts
        )

        contracts_json = [
            await request.app.loop.run_in_executor(
                request.app.thread_pool, lambda: Contract(contract_id).contracts
            ) for contract_id in contracts_ids
        ]

        response = {
            'count': len(contracts_json),
            'data': contracts_json
        }
        response.update(links)
        return json(response)


bp_modcontracts.add_route(
    ModContractsView.as_view(),
    '/modcontracts/',
    name='get_modcontracts',
)
