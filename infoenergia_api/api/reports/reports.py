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
        request.ctx.user = user

        report_ids = await request.app.loop.create_task(get_report_ids(request))

        # status = await request.app.loop.create_task(
        #     beedataApi().process_reports(jsonlib.loads(report_ids))
        # )

        status = 200
        return json(status)


bp_reports.add_route(
    ReportsView.as_view(),
    '/reports',
    name='reports',
)