from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import protected, inject_user

from infoenergia_api.contrib import BeedataReports, PaginationLinksMixin, ResponseMixin
from infoenergia_api.contrib.beedata_api import BeedataApiMixin

from .models import create_report_request

bp_reports = Blueprint("reports")


class ReportsView(ResponseMixin, PaginationLinksMixin, BeedataApiMixin, HTTPMethodView):
    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "reports.reports"

    async def post(self, request, user):
        try:
            body = request.json
            if not body:
                return self.empty_body_response()

            report_request = await create_report_request(request.id, request.body)

            beedata_reports = BeedataReports(
                await self.bapi,
                request.app.ctx.mongo_client,
                report_request,
            )
            request.app.loop.create_task(beedata_reports.process_reports())
        except Exception as e:
            return self.unexpected_error_response(e)
        else:
            response = {
                "reports": len(beedata_reports.reports),
                "request_id": request.id.hex,
            }
            return self.succesfull_response(response)


bp_reports.add_route(
    ReportsView.as_view(),
    "/reports",
    name="reports",
)
