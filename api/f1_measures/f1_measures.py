import asyncio
import json as json_basic

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from ..tasks import async_get_invoices, async_get_f1_measures_json

bp_f1_measures = Blueprint('f1')


class F1MeasuresContractIdView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, contractId):
        app = request.app
        sem = asyncio.Semaphore(app.config.MAX_TASKS)
        invoices = await async_get_invoices(request, contractId)
        logger.info('There are %d invoices', len(invoices))
        logger.info('*' * 100)

        f1_measure_json = [
            await async_get_f1_measures_json(
                app.loop,
                app.thread_pool,
                app.erp_client,
                sem,
                invoice
            )
            for invoice in invoices
        ]
        return json(f1_measure_json)


class F1MeasuresView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request):
        app = request.app
        sem = asyncio.Semaphore(app.config.MAX_TASKS)
        result = []
        invoices = await async_get_invoices(request)

        to_do = [
             async_get_f1_measures_json(
                app.loop,
                app.thread_pool,
                app.erp_client,
                sem,
                invoice
            )
            for invoice in invoices
        ]
        while to_do:
            logger.info("%d invoices to anonymize", len(to_do))
            done, to_do = await asyncio.wait(to_do, timeout=app.config.TASK_TIMEOUT)
            for task in done:
                try:
                    f1_measure_json = task.result()
                except Exception as e:
                    logger.error("Reason: %s", str(e))
                else:
                    result.append(f1_measure_json)
        return json(result)


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
