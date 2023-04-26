import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import inject_user, protected

from config import config
from infoenergia_api.contrib import PaginationLinksMixin
from infoenergia_api.contrib.cch import (
    async_get_cch,
    get_measures,
    curve_types,
)
from infoenergia_api.contrib.mixins import ResponseMixin
from infoenergia_api.contrib.pagination import PageNotFoundError

bp_cch_measures = Blueprint("cch")


class ModelNotFoundError(Exception):
    code = "cch_model_not_found"


class BaseCchMeasuresContractView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):
    async def get_cch_ids(self, request, contract_id=None):
        cchs, links, total_results = await self.paginate_results(
            request, function=async_get_cch, contract_id=contract_id
        )
        return cchs, links, total_results

    async def get_cch_measures(self, cchs, user, contract_id=None, curve_type=None):
        return await asyncio.gather(*[
            get_measures(curve_type, cch, contract_id, user) for cch in cchs
        ])

class CchMeasuresContractIdView(BaseCchMeasuresContractView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "cch.get_cch_measures_by_contract_id"

    async def get(self, request, contract_id, user):
        logger.info("Getting cch measures for contract: %s", contract_id)
        request.ctx.user = user

        curve_type = request.args.get('type', '')
        try:
            if curve_type not in curve_types:
                raise ModelNotFoundError()
            cchs, links, total_results = await self.get_cch_ids(request, contract_id)
        except (PageNotFoundError, ModelNotFoundError) as e:
            return self.error_response(e)
        else:
            cch_measures = await self.get_cch_measures(
                cchs, user, contract_id, curve_type=curve_type,
            )
            response = {
                "total_results": total_results,
                "count": len(cch_measures),
                "data": cch_measures,
            }
            response.update(links)
            return json(response)


class CchMeasuresView(BaseCchMeasuresContractView):

    decorators = [
        inject_user(),
        protected(),
    ]

    endpoint_name = "cch.get_cch_measures"

    async def get(self, request, user):
        request.ctx.user = user
        logger.info("Getting cch measures")
        curve_type = request.args.get('type', '')
        try:
            if curve_type not in curve_types:
                raise ModelNotFoundError()
            cchs, links, total_results = await self.get_cch_ids(request)
        except (PageNotFoundError, ModelNotFoundError) as e:
            return self.error_response(e)
        else:
            cch_measures = await self.get_cch_measures(
                cchs, user, curve_type=curve_type
            )
            response = {
                "total_results": total_results,
                "count": len(cch_measures),
                "data": cch_measures,
            }
            response.update(links)
            return json(response)


bp_cch_measures.add_route(
    CchMeasuresView.as_view(),
    "/cch/",
    name="get_cch_measures",
)

bp_cch_measures.add_route(
    CchMeasuresContractIdView.as_view(),
    "/cch/<contract_id>",
    name="get_cch_measures_by_contract_id",
)
