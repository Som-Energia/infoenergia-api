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
                    tariff_price_filters, int(tariff_price_id))
                    for tariff_price_id in tariff_price_filters["tariffPriceId"]
            ]
            base_response = {"total_results": total_results, **links}
            response_body = await self.make_response_body(request, tariff_prices, base_response)
            return json(response_body)


bp_tariff.add_route(
    TariffView.as_view(),
    "/tariff/",
    name="get_tariff",
)