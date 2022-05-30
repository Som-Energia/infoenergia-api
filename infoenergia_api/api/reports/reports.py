from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_ext import validate
from sanic_jwt.decorators import protected, inject_user
from infoenergia_api.api.reports.validators import ReportsBody

from infoenergia_api.contrib import Beedata, PaginationLinksMixin, ResponseMixin
from infoenergia_api.beedata_api import BeedataApiMixin

bp_reports = Blueprint('reports')


class ReportsView(ResponseMixin, PaginationLinksMixin, BeedataApiMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'reports.reports'

    @validate(ReportsBody)
    async def post(self, request, user):
        try:
            body = request.json
            if not body:
                return self.empty_body_response()
        except Exception as e:
            return self.unexpected_error_response(e)
        else:
            request.app.loop.create_task(
                Beedata(
                    self.bapi, request.app.ctx.mongo_client, request.app.ctx.redis
                ).process_reports(body['contract_ids'], body['month'], body['report_type'])
            )
            response = {
                'reports': len(body['contract_ids']),
            }
            return json(response)


bp_reports.add_route(
    ReportsView.as_view(),
    '/reports',
    name='reports',
)
