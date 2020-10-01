from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected, inject_user

from infoenergia_api.contrib.contracts import async_get_contracts, Contract
from infoenergia_api.contrib import PaginationLinksMixin

bp_contracts = Blueprint('contracts')


class ContractsIdView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'contracts.get_contract_by_id'

    async def get(self, request, contractId, user):
        logger.info("Getting contracts")
        request.ctx.user = user
        contracts_ids, links = await self.paginate_results(
            request, function=async_get_contracts, contractId=contractId
        )

        contract_json = [await request.app.loop.run_in_executor(
                request.app.thread_pool, lambda: Contract(contract_id).contracts
            ) for contract_id in contracts_ids
        ]

        response = {
            'count': len(contract_json),
            'data': contract_json
        }
        response.update(links)
        return json(response)


class ContractsView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'contracts.get_contracts'

    async def get(self, request, user):
        logger.info("Getting contracts")
        request.ctx.user = user
        contracts_ids, links = await self.paginate_results(
            request,
            function=async_get_contracts
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


bp_contracts.add_route(
    ContractsView.as_view(),
    '/contracts/',
    name='get_contracts',
)

bp_contracts.add_route(
    ContractsIdView.as_view(),
    '/contracts/<contractId>',
    name='get_contract_by_id'
)
