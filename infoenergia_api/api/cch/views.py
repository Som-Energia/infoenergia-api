import asyncio

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt.decorators import inject_user, protected

from config import config
from infoenergia_api.contrib import PaginationLinksMixin
from infoenergia_api.contrib.cch import (
    cch_model,
    TgCchF1,
    TgCchF5d,
    TgCchP1,
    TgCchVal,
    TgCchGennetabeta,
    TgCchAutocons,
    async_get_cch,
    get_measures,
)
from infoenergia_api.contrib.mixins import ResponseMixin
from infoenergia_api.contrib.pagination import PageNotFoundError

bp_cch_measures = Blueprint("cch")


class ModelNotFoundError(Exception):
    code = "cch_model_not_found"


class BaseCchMeasuresContractView(ResponseMixin, PaginationLinksMixin, HTTPMethodView):
    async def get_cch_ids(self, request, contract_id=None):
        cch_ids, links, total_results = await self.paginate_results(
            request, function=async_get_cch, contract_id=contract_id
        )
        return cch_ids, links, total_results

    async def get_cch_measures(self, model, cch_ids, user, contract_id=None, curve_type=None):
        if curve_type in ['tg_cchfact']:
            cchs = cch_ids # TODO: we are getting cch's no ids for those curves
            return await asyncio.gather(*[
                get_measures(curve_type, cch, contract_id, user) for cch in cchs
            ])

        measures = []
        loop = asyncio.get_running_loop()
        to_do = [loop.create_task(model.create(cch_id)) for cch_id in sorted(cch_ids)]

        while to_do:
            done, to_do = await asyncio.wait(to_do, timeout=config.TASKS_TIMEOUT)
            for task in done:
                curve = task.result()
                measures.append(await curve.cch_measures(user, contract_id))
        return measures


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
            model = cch_model(curve_type)
            if not model:
                raise ModelNotFoundError()

            cch_ids, links, total_results = await self.get_cch_ids(request, contract_id)
        except (PageNotFoundError, ModelNotFoundError) as e:
            return self.error_response(e)
        else:
            cch_measures = await self.get_cch_measures(
                model, cch_ids, user, contract_id, curve_type=curve_type,
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
            model = cch_model(curve_type)
            if not model:
                raise ModelNotFoundError()

            cch_ids, links, total_results = await self.get_cch_ids(request)
        except (PageNotFoundError, ModelNotFoundError) as e:
            return self.error_response(e)
        else:
            cch_measures = await self.get_cch_measures(
                model, cch_ids, user, curve_type=curve_type
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
