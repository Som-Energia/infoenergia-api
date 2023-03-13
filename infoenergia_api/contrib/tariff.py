import asyncio
import functools
import itertools
import operator
from sanic.log import logger

from ..contrib.erp import get_erp_instance
from ..utils import get_request_filters

from infoenergia_api.contrib import ResponseMixin


class TariffPrice(ResponseMixin, object):

    def __init__(self, tariff_id, filters):
        logger.debug("Creating object for tariff %d", tariff_id)

        self._erp = get_erp_instance()
        self._Tariff = self._erp.model('giscedata.polissa.tarifa')

        self.filters = filters
        self.tariff_id = tariff_id

    @classmethod
    async def create(cls, tarif_id, filters):
        loop = asyncio.get_running_loop()
        self = await loop.run_in_executor(
            None, cls, tarif_id, filters
        )
        return self

    @property
    def reactiveEnergy(self):

        price_version = self._PricelistItem.read(
            [
                ("name", "like", "%Cos%"),
                ("base_pricelist_id", "=", 3),
            ],
            ["price_version_id"],
            order="price_version_id",


    @property
    def get_erp_tariff_prices(self):
        prices = self._Tariff.get_tariff_prices(
            self.tariff_id,
            self.filters.get('municipi_id', 3830),
            self.filters.get('max_power', 5000),
            self.filters.get('fiscal_position', None),
            self.filters.get('with_taxes', False),
            self.filters.get('date_from', False),
            self.filters.get('date_to', False)
        )

        if any(d.get('error', False) for d in prices):
            return prices[0]
        else:
            price_detail = [
                {
                    "dateStart": price["start_date"],
                    "dateEnd": price["end_date"],
                    "activeEnergy": price["energia"],
                    "power": price["potencia"],
                    "GKWh": price["generation_kWh"],
                    "autoconsumo": price["energia_autoconsumida"],
                    "meter": price["comptador"],
                    "bonoSocial": price["bo_social"],
                    "reactiveEnergy": price["reactiva"]
                }
                for price in sorted(prices, key=lambda x: x['start_date'], reverse=True)
            ]

            if price_detail[0]['dateEnd']:
                return {
                    "current": {},
                    "history": price_detail
                }

            else:
                return {
                    "current": price_detail[0],
                    "history": price_detail[1:]
                }

    @property
    def tariff(self):
        return {
            "tariffPriceId": self.tariff_id,
            "price": self.get_erp_tariff_prices,
        }

    def __iter__(self):
        yield from self.tariff.items()

def get_tariff_prices(request, contract_id=None):
    tariff_obj = request.app.ctx.erp_client.model("giscedata.polissa.tarifa")
    contract_obj = request.app.ctx.erp_client.model("giscedata.polissa")
    erp_filters = [
        ("active", "=", True),
    ]
    if request.args:
        filters = { key: value for (key, value) in request.args.items()}

        if "tariffPriceId" in request.args:
            return filters
        elif "type" in request.args:
            erp_filters += [
                ("name", "=", request.args["type"][0]),
            ]
            tariff_id = tariff_obj.search(erp_filters)
            filters["tariffPriceId"] = tariff_id
            return filters
    if contract_id:
        tariff_price_id = contract_obj.read(
            [("name", "=", contract_id)], ["llista_preu"]
        )[0]["llista_preu"][0]
        return [tariff_price_id]

    tariff_id = tariff_obj.search(filters)
    tariff_price_ids = [
        price["llistes_preus_comptatibles"] for price in tariff_obj.read(tariff_id)
    ]
    return list(set(functools.reduce(operator.concat, tariff_price_ids)))


    tariff_ids = tariff_obj.search(erp_filters)
    filters["tariffPriceId"] = tariff_ids
    return filters


async def async_get_tariff_prices(request, contract_id=None):
    try:
        tariff = await request.app.loop.run_in_executor(
            None,
            functools.partial(get_tariff_prices, request, contract_id),
        )
    except Exception as e:
        raise e
    return tariff
