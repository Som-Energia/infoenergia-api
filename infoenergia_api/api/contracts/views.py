from infoenergia_api.contrib import (
    Contract,
    TariffPrice,
    PageNotFoundError,
    PaginationLinksMixin,
    ResponseMixin,
)
from infoenergia_api.contrib.contracts import async_get_contracts
from infoenergia_api.contrib.tariff import async_get_tariff_prices, get_tariff_filters

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import inject_user, protected

bp_contracts = Blueprint("contracts")


class ContractsIdView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "contracts.get_contract_by_id"

    async def get(self, request, contract_id, user):
        logger.info(f"Getting contract information for contract {contract_id}")
        request.ctx.user = user

        try:
            contracts_ids, links, total_results = await self.paginate_results(
                request, function=async_get_contracts, contract_id=contract_id
            )
        except PageNotFoundError as e:
            return self.error_response(e)

        else:
            contracts = [
                await Contract.create(contract_id) for contract_id in contracts_ids
            ]

            base_response = {"total_results": total_results, **links}
            response_body = await self.make_response_body(
                request, contracts, base_response
            )
            return json(response_body)


class ContractsView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "contracts.get_contracts"

    async def get(self, request, user):
        logger.info("Getting contracts")
        request.ctx.user = user
        try:
            contracts_ids, links, total_results = await self.paginate_results(
                request, function=async_get_contracts
            )
        except PageNotFoundError as e:
            return self.error_response(e)

        contracts = [
            await Contract.create(contract_id) for contract_id in contracts_ids
        ]
        base_response = {"total_results": total_results, **links}
        response_body = await self.make_response_body(request, contracts, base_response)

        return json(response_body)


class ContractsIdTariffView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "contracts.get_contract_by_id_tariff"

    async def get(self, request, contract_id, user):
        request.ctx.user = user
        logger.info("Getting tariffs")

        try:
            contracts_ids, links, total_results = await self.paginate_results(
                request, function=async_get_contracts, contract_id=contract_id
            )

        except PageNotFoundError as e:
            return self.error_response(e)

        else:
            tariff_price_filters = get_tariff_filters(request, contract_id=contracts_ids)

            tariff_price_ids, links, total_results = await self.paginate_results(
                request, function=async_get_tariff_prices
            )
            tariff_prices = [
                await TariffPrice.create(tariff_price_filters, tariff_price_ids)
            ]

            base_response = {"total_results": total_results, **links}
            response_body = await self.make_response_body(request, tariff_prices, base_response)
            return json(response_body)



bp_contracts.add_route(
    ContractsView.as_view(),
    "/contracts/",
    name="get_contracts",
)

bp_contracts.add_route(
    ContractsIdView.as_view(),
    "/contracts/<contract_id>",
    name="get_contract_by_id"
)

bp_contracts.add_route(
    ContractsIdTariffView.as_view(),
    "/contracts/<contract_id>/tariff",
    name="get_contract_by_id_tariff"
)
