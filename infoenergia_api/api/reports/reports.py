from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected, inject_user

from infoenergia_api.contrib import Beedata, get_report_ids, PaginationLinksMixin
from infoenergia_api.beedata_api import BeedataApiMixin

bp_reports = Blueprint('reports')

class ReportsView(PaginationLinksMixin, BeedataApiMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'reports.reports'

    async def post(self, request, user):
        logger.info("Uploading contracts")
        report_ids, month, report_type = await get_report_ids(request)

        request.app.loop.create_task(
            Beedata(self.bapi, request.app.ctx.mongo_client, request.app.ctx.redis).process_reports(report_ids, month, report_type)
        )
        response = {
            'reports': len(report_ids),
        }
        return json(response)


bp_reports.add_route(
    ReportsView.as_view(),
    '/reports',
    name='reports',
)
