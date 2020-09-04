import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.tariff import async_get_tariff_prices, Tariff
from infoenergia_api.contrib import Pagination, PaginationLinksMixin

bp_tariff = Blueprint('tariff')


class TariffView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        protected(),
    ]

    endpoint_name = 'tariff.get_tariff'

    async def get(self, request):
        logger.info("Getting tariffs")
        tariff_price_ids, links = await self.paginate_results(
            request,
            function=async_get_tariff_prices
        )

        tariff_json = [
            await request.app.loop.run_in_executor(
                request.app.thread_pool, lambda: Tariff(tariff_price_id).tariff
            ) for tariff_price_id in tariff_price_ids
        ]

        response = {
            'count': len(tariff_json),
            'data': tariff_json
        }
        response.update(links)
        return json(response)


bp_tariff.add_route(
    TariffView.as_view(),
    '/tariff/',
    name='get_tariff',
)
