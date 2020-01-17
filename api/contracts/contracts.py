import asyncio
import json as json_basic

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from ..tasks import async_get_contract_json, async_get_contracts

bp_contracts = Blueprint('contracts')


class ContractsIdView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, contractId):
        contract = await async_get_contracts(request, contractId)
        contract_json = await async_get_contract_json(
            request.app.loop,
            request.app.thread_pool,
            request.app.erp_client,
            contract
        )
        return json(contract_json)


class ContractsView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request):
        app = request.app
        contracts = await async_get_contracts(request)
        logger.info('how many contracts: %d', len(contracts))

        contracts_json = [
            await async_get_contract_json(
                asyncio.get_event_loop(),
                app.thread_pool,
                app.erp_client,
                contract
            )
            for contract in contracts
        ]
        return json(contracts_json)


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
