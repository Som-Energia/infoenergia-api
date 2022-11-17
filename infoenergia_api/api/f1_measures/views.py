from base64 import urlsafe_b64encode, urlsafe_b64decode

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import inject_user, protected

from infoenergia_api.contrib.f1 import async_get_invoices, Invoice
from infoenergia_api.contrib import PaginationLinksMixin
from infoenergia_api.contrib.mixins import ResponseMixin
from infoenergia_api.contrib.pagination import PageNotFoundError

bp_f1_measures = Blueprint("f1")


class F1MeasuresContractIdView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "f1.get_f1_measures_by_contract_id"

    async def get(self, request, contractId, user):
        logger.info("Getting f1 measures for contract: %s", contractId)
        request.ctx.user = user

        try:
            invoices_ids, links, total_results = await self.paginate_results(
                request, function=async_get_invoices, contractId=contractId
            )
        except PageNotFoundError as e:
            return self.error_response(e)
        else:
            invoices = [await Invoice.create(invoice_id) for invoice_id in invoices_ids]

            base_response = {"total_results": total_results, **links}
            response_body = await self.make_response_body(
                request, invoices, base_response
            )
            return json(response_body)


class F1MeasuresView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "f1.get_f1_measures"

    async def get(self, request, user):
        logger.info("Getting f1 measures")
        request.ctx.user = user
        try:
            invoices_ids, links, total_results = await self.paginate_results(
                request, function=async_get_invoices
            )
        except PageNotFoundError as e:
            return self.error_response(e)
        else:
            invoices = [await Invoice.create(invoice_id) for invoice_id in invoices_ids]

            base_response = {"total_results": total_results, **links}
            response_body = await self.make_response_body(
                request, invoices, base_response
            )
            return json(response_body)


bp_f1_measures.add_route(
    F1MeasuresView.as_view(),
    "/f1/",
    name="get_f1_measures",
)

bp_f1_measures.add_route(
    F1MeasuresContractIdView.as_view(),
    "/f1/<contractId>",
    name="get_f1_measures_by_contract_id",
)
