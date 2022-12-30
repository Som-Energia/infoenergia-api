import functools
import itertools
import operator
from sanic.log import logger

from ..utils import get_request_filters, make_uuid


class ReactiveEnergyPrice(object):
    @classmethod
    def create(cls):
        from infoenergia_api.app import app

        self = cls()
        self._erp = app.ctx.erp_client
        self._PricelistItem = self._erp.model("product.pricelist.item")
        return self

    def reactiveEnergyPrice(self, price_version_id, name):

        priceitem_ids = self._PricelistItem.search(
            [
                ("name", "like", "%Cos%"),
                ("base_pricelist_id", "=", 3),
                ("price_version_id", "=", price_version_id),
                ("name", "=", name),
            ]
        )
        return self._PricelistItem.read(priceitem_ids)[0]["price_surcharge"]

    @property
    def reactiveEnergy(self):

        price_version = self._PricelistItem.read(
            [
                ("name", "like", "%Cos%"),
                ("base_pricelist_id", "=", 3),
            ],
            ["price_version_id"],
            order="price_version_id",
        )

        boe_prices = [pv["price_version_id"] for pv in price_version]

        reactive_prices = [
            boe_prices for boe_prices, _ in itertools.groupby(boe_prices)
        ]
        price_detail = [
            {
                "BOE": rp[1],
                "price33": self.reactiveEnergyPrice(rp[0], str("Cos(fi) 0.80 - 0.95")),
                "price75": self.reactiveEnergyPrice(rp[0], str("Cos(fi) 0 - 0.80")),
                "units": "€/kVArh",
            }
            for rp in reactive_prices
        ]
        return {
            "priceReactiveEnergy": {
                "current": price_detail[-1],
                "history": price_detail[:-1],
            }
        }


class TariffPrice(object):
    FIELDS = ["id", "version_id", "type"]

    def __init__(self, price_id):
        from infoenergia_api.app import app

        self._erp = app.ctx.erp_client
        self._Priceversion = self._erp.model("product.pricelist.version")
        self._Pricelist = self._erp.model("product.pricelist")
        self._PricelistItem = self._erp.model("product.pricelist.item")

        for name, value in self._Pricelist.read(price_id, self.FIELDS).items():
            setattr(self, name, value)

    def termPrice(self, items_id, term_type, units):
        """
        Term price
         [{
         'period': P1
         'price': 0.139
         'units': €/kWh
         }]
        """
        fields = [
            "name",
            "base_price",
            "price_discount",
            "price_surcharge",
        ]
        term_price = self._PricelistItem.read(items_id, fields)
        if term_type == "GKWh":
            return [
                {
                    "period": tp["name"].split(" ")[1]
                    if "2.0TD" in tp["name"]
                    else tp["name"].split("_")[0],
                    "price": tp["base_price"] * (1 + tp["price_discount"])
                    + tp["price_surcharge"],
                    "units": units,
                }
                for tp in term_price
                if tp["name"].find(term_type) > 0
                if "P3" not in tp["name"]
            ]
        else:
            return [
                {
                    "period": tp["name"].split(" ")[1]
                    if "2.0TD" in tp["name"]
                    else tp["name"].split("_")[0],
                    "price": tp["base_price"] * (1 + tp["price_discount"])
                    + tp["price_surcharge"],
                    "units": units,
                }
                for tp in term_price
                if tp["name"].find(term_type) > 0
            ]

    @property
    def priceDetail(self):
        """
        Tariff prices
         2020-06-01
        """
        fields = [
            "date_start",
            "date_end",
            "items_id",
        ]
        prices = self._Priceversion.read(self.version_id, fields, order="date_start")

        if prices:
            price_detail = [
                {
                    "dateStart": price["date_start"],
                    "dateEnd": price["date_end"],
                    "activeEnergy": self.termPrice(
                        price["items_id"], "ENERGIA", "€/kWh"
                    ),
                    "power": self.termPrice(price["items_id"], "POTENCIA", "€/kW year"),
                    "GKWh": self.termPrice(price["items_id"], "GKWh", "€/kWh"),
                }
                for price in prices
            ]
            return {"current": price_detail[0], "history": price_detail[1:]}

    @property
    def tariff(self):
        if self.type == "sale":
            return {
                "tariffPriceId": self.id,
                "price": self.priceDetail,
            }


def get_tariff_prices(request, contract_id=None):
    tariff_obj = request.app.ctx.erp_client.model("giscedata.polissa.tarifa")
    contract_obj = request.app.ctx.erp_client.model("giscedata.polissa")
    filters = [
        ("active", "=", True),
    ]
    if request.args:
        if "tariffPriceId" in request.args:
            return [int(request.args["tariffPriceId"][0])]
        else:
            filters = get_request_filters(
                request.app.ctx.erp_client,
                request,
                filters,
            )

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


async def async_get_tariff_prices(request, contract_id=None):
    try:
        tariff = await request.app.loop.run_in_executor(
            None,
            functools.partial(get_tariff_prices, request, contract_id),
        )
    except Exception as e:
        raise e
    return tariff
