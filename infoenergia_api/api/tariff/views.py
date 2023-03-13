import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

from infoenergia_api.contrib import(
    TariffPrice,
    PageNotFoundError,
    PaginationLinksMixin,
    ResponseMixin,
)

from infoenergia_api.contrib.tariff import async_get_tariff_prices

bp_tariff = Blueprint("tariff")


class TariffView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):
    decorators = [
        protected(),
    ]

    endpoint_name = "tariff.get_tariff"

    async def get(self, request):
        logger.info("Getting tariffs")
        try:
            tariff_price_filters, links, total_results = await self.paginate_results(
                request, function=async_get_tariff_prices
            )
        except PageNotFoundError as e:
            return self.error_response(e)

        else:
            tariff_prices = [
                await TariffPrice.create(
                    int(tariff_price_id), tariff_price_filters)
                    for tariff_price_id in tariff_price_filters["tariffPriceId"]
            ]
            base_response = {"total_results": total_results, **links}
            response_body = await self.make_response_body(request, tariff_prices, base_response)
            return json(response_body)


class TariffContractIdView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        protected(),
    ]

    endpoint_name = "tariff.get_tariff_by_contract_id"

    async def get(self, request, contract_id):
        logger.info("Getting tariffs")
        tariff_price_ids, links, total_results = await self.paginate_results(
            request, function=async_get_tariff_prices, contract_id=contract_id
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
    "/tariff/<contract_id>",
    name="get_tariff_by_contract_id",
)
