from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected, inject_user

from infoenergia_api.contrib import Beedata, BeedataApiClient, get_report_ids, PaginationLinksMixin


bp_reports = Blueprint('reports')

class ReportsView(PaginationLinksMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = 'reports.reports'

    async def post(self, request, user):
        logger.info("Uploading contracts")
        report_ids, month, report_type = await get_report_ids(request)

        bapi = await BeedataApiClient.create(
            url=request.app.config.BASE_URL,
            username=request.app.config.USERNAME,
            password=request.app.config.PASSWORD,
            company_id=request.app.config.COMPANY_ID,
            cert_file=request.app.config.CERT_FILE,
            cert_key=request.app.config.KEY_FILE
        )
        request.app.loop.create_task(
            Beedata(bapi, request.app.mongo_client, request.app.redis).process_reports(report_ids, month, report_type)
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
