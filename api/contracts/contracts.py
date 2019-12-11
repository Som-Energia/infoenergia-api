import configdb
from api.tasks import get_contract_json, get_contracts
from erppeek import Client
from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected

bp_contracts = Blueprint('contracts')


class ContractsIdView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, contractId):
        erp_client = Client(**configdb.erppeek)
        contract = get_contracts(request, erp_client, contractId)
        contract_json = get_contract_json(erp_client, contract)
        return json(contract_json)


class ContractsView(HTTPMethodView):
    decorators = [
        protected(),
    ]

    async def get(self, request, *args, **kwargs):
        erp_client = Client(**configdb.erppeek)
        contracts = get_contracts(request, erp_client)
        logger.info('how many contracts: {}'.format(len(contracts)))
        contract_json = []
        for contract in contracts:
            contract_json.append(get_contract_json(erp_client, contract))
        return json(contract_json)


bp_contracts.add_route(
    ContractsView.as_view(),
    '/contracts/',
)

bp_contracts.add_route(
    ContractsIdView.as_view(),
    '/contracts/<contractId>',
)
