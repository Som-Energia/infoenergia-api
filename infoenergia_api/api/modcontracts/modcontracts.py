import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.contracts import async_get_contract_json
from infoenergia_api.contrib.modcontracts import async_get_modcontracts

bp_modcontracts = Blueprint('modcontracts')


class ModContractsView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request):
        app = request.app
        sem = asyncio.Semaphore(app.config.MAX_TASKS)
        result = []
        contracts = await async_get_modcontracts(request)
        logger.debug("how many contracts: %d", len(contracts))

        to_do = [
            async_get_contract_json(
                app.loop, app.thread_pool, app.erp_client, sem, contract
            )
            for contract in contracts
        ]
        while to_do:
            logger.debug("%d contracts to anonymize", len(to_do))
            done, to_do = await asyncio.wait(to_do, timeout=app.config.TASK_TIMEOUT)
            for task in done:
                try:
                    contract_json = task.result()
                except Exception as e:
                    logger.error("Reason: %s", str(e))
                else:
                    result.append(contract_json)
        return json(result)


bp_modcontracts.add_route(
    ModContractsView.as_view(),
    '/modcontracts/',
    name='get_modcontracts',
)
