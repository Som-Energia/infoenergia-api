from infoenergia_api.contrib import (
    Contract,
    PageNotFoundError,
    PaginationLinksMixin,
    ResponseMixin,
)
from infoenergia_api.contrib.contracts import async_get_contracts
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

    async def get(self, request, contractId, user):
        logger.info(f"Getting contract information for contract {contractId}")
        request.ctx.user = user

        try:
            contracts_ids, links, total_results = await self.paginate_results(
                request, function=async_get_contracts, contractId=contractId
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


bp_contracts.add_route(
    ContractsView.as_view(),
    "/contracts/",
    name="get_contracts",
)

bp_contracts.add_route(
    ContractsIdView.as_view(), "/contracts/<contractId>", name="get_contract_by_id"
)
