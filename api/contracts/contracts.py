from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import json

bp_contracts = Blueprint('contracts')


class ContractsView(HTTPMethodView):

    async def get(self, request):
        return json({'hola': 'caracola'})

bp_contracts.add_route(ContractsView.as_view(), '/contracts', methods=['GET'])
