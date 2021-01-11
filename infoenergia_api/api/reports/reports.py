from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected, inject_user

from infoenergia_api.contrib import beedataApi, get_report_ids
from infoenergia_api.contrib import PaginationLinksMixin


bp_reports = Blueprint('reports')

class ReportsView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'reports.reports'

    async def post(self, request, user):
        logger.info("Uploading contracts")
        report_ids = await request.app.loop.create_task(get_report_ids(request))

        unprocessed_reports = await request.app.loop.create_task(
            beedataApi().process_reports(report_ids)
         )

        response = {
            'reports': len(report_ids),
            'unprocessed_reports': unprocessed_reports
        }
        return json(response)


bp_reports.add_route(
    ReportsView.as_view(),
    '/reports',
    name='reports',
)
