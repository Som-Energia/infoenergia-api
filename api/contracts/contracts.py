import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from ..contrib.contrib_contracts import (async_get_contract_json,
                                         async_get_contracts)

bp_contracts = Blueprint('contracts')


class ContractsIdView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, contractId):
        app = request.app
        sem = asyncio.Semaphore(app.config.MAX_TASKS)
        contract = await async_get_contracts(request, contractId)
        contract_json = await async_get_contract_json(
            app.loop,
            app.thread_pool,
            app.erp_client,
            sem,
            contract
        )
        return json(contract_json)


class ContractsView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request):
        app = request.app
        sem = asyncio.Semaphore(app.config.MAX_TASKS)
        result = []
        contracts = await async_get_contracts(request)
        logger.info("how many contracts: %d", len(contracts))

        to_do = [
            async_get_contract_json(
                app.loop, app.thread_pool, app.erp_client, sem, contract
            )
            for contract in contracts
        ]
        while to_do:
            logger.info("%d contracts to anonymize", len(to_do))
            done, to_do = await asyncio.wait(to_do, timeout=app.config.TASK_TIMEOUT)
            for task in done:
                try:
                    contract_json = task.result()
                except Exception as e:
                    logger.error("Reason: %s", str(e))
                else:
                    result.append(contract_json)

        return json(result)


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
