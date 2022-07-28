import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib.tariff import (
    async_get_tariff_prices,
    TariffPrice,
    ReactiveEnergyPrice,
)
from infoenergia_api.contrib import Pagination, PaginationLinksMixin

bp_tariff = Blueprint("tariff")


class TariffView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        protected(),
    ]

    endpoint_name = "tariff.get_tariff"

    async def get(self, request):
        logger.info("Getting tariffs")
        tariff_price_ids, links, total_results = await self.paginate_results(
            request, function=async_get_tariff_prices
        )

        tariff_json = list(
            filter(
                None,
                [
                    await request.app.loop.run_in_executor(
                        request.app.ctx.thread_pool,
                        lambda: TariffPrice(tariff_price_id).tariff,
                    )
                    for tariff_price_id in tariff_price_ids
                ],
            )
        )

        tariff_results = len(tariff_json)

        reactive_energy_json = ReactiveEnergyPrice.create().reactiveEnergy
        tariff_json.append(reactive_energy_json)

        response = {"count": tariff_results, "data": tariff_json}
        response.update(links)
        return json(response)


class TariffContractIdView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        protected(),
    ]

    endpoint_name = "tariff.get_tariff_by_contract_id"

    async def get(self, request, contractId):
        logger.info("Getting tariffs")
        tariff_price_ids, links, total_results = await self.paginate_results(
            request, function=async_get_tariff_prices, contractId=contractId
        )

        tariff_json = list(
            filter(
                None,
                [
                    await request.app.loop.run_in_executor(
                        request.app.ctx.thread_pool,
                        lambda: TariffPrice(tariff_price_id).tariff,
                    )
                    for tariff_price_id in tariff_price_ids
                ],
            )
        )

        tariff_results = len(tariff_json)

        reactive_energy_json = ReactiveEnergyPrice.create().reactiveEnergy
        tariff_json.append(reactive_energy_json)

        response = {"count": tariff_results, "data": tariff_json}
        response.update(links)
        return json(response)


bp_tariff.add_route(
    TariffView.as_view(),
    "/tariff/",
    name="get_tariff",
)

bp_tariff.add_route(
    TariffContractIdView.as_view(),
    "/tariff/<contractId>",
    name="get_tariff_by_contract_id",
)
