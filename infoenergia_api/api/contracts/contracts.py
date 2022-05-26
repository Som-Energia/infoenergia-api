from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import inject_user, protected

from infoenergia_api.contrib import (ContractResponseMixin,
                                     PaginationLinksMixin)
from infoenergia_api.contrib.contracts import async_get_contracts

bp_contracts = Blueprint('contracts')


class ContractsIdView(ContractResponseMixin, PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'contracts.get_contract_by_id'

    async def get(self, request, contractId, user):
        logger.info(f"Getting contract information for contract {contractId}")
        request.ctx.user = user
        contracts_ids, links, total_results = await self.paginate_results(
            request, function=async_get_contracts, contractId=contractId
        )

        contract_response = await self.get_response_contracts(request, contracts_ids)

        response = {
            'total_results': total_results,
        }
        response.update(contract_response)
        response.update(links)
        return json(response)


class ContractsView(ContractResponseMixin, PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'contracts.get_contracts'

    async def get(self, request, user):
        logger.info("Getting contracts")
        request.ctx.user = user
        contracts_ids, links, total_results = await self.paginate_results(
            request,
            function=async_get_contracts
        )

        contracts_response = await self.get_response_contracts(request, contracts_ids)

        response = {
            'total_results': total_results,
        }
        response.update(contracts_response)
        response.update(links)
        return json(response)



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
