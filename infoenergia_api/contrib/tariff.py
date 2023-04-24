import asyncio
import functools
from sanic.log import logger

from ..contrib.erp import get_erp_instance


class TariffPrice(object):

    geographical_region = {
        "canarias": 1646,
        "peninsula": 3830
    }

    def __init__(self, filters, tariff_id=None):
        logger.debug("Creating object for tariff %d", tariff_id)

        self._erp = get_erp_instance()
        self._Tariff = self._erp.model('giscedata.polissa.tarifa')

        self.filters = filters
        self.tariff_id = tariff_id
        self.contract_id = filters.get('contract_id', None)

    @classmethod
    async def create(cls, filters, tarif_id=None):
        loop = asyncio.get_running_loop()
        self = await loop.run_in_executor(
            None, cls, filters, tarif_id
        )
        return self

    @property
    def get_erp_tariff_prices(self):

        if self.contract_id:
            return self._Tariff.get_tariff_prices_by_contract_id_www(
                self.contract_id[0],
                self.filters.get('withTaxes', False),
            )
        else:
            return self._Tariff.get_tariff_prices_www(
                self.tariff_id,
                self.geographical_region[
                    self.filters.get('geographicalRegion', 'peninsula')
                ],
                self.filters.get('max_power', None),
                self.filters.get('fiscal_position_id', None),
                self.filters.get('withTaxes', False),
                self.filters.get('home', False),
                self.filters.get('from_', False),
                self.filters.get('to_', False)
            )

    @property
    def tariff_format(self):
        return {
            "dateStart": self.price_data["start_date"],
            "dateEnd": self.price_data["end_date"],
            "activeEnergy": dict(sorted(self.price_data["energia"].items())),
            "power":  dict(sorted(self.price_data["potencia"].items())),
            "gkwh": dict(sorted(self.price_data["generation_kWh"].items())),
            "autoconsumo": dict(sorted(self.price_data["energia_autoconsumida"].items())),
            "meter": self.price_data["comptador"],
            "bonoSocial": self.price_data["bo_social"],
            "reactiveEnergy": dict(sorted(self.price_data["reactiva"].items())),
            "taxes": {
                "name": self.price_data['fiscal_position']['name'],
                "dateStart": self.price_data['fiscal_position']['date_from'],
                "dateEnd": self.price_data['fiscal_position']['date_to'],
            } if self.price_data['fiscal_position'] else {}

        } if self.price_data else {}


    def to_tariff_format(self, tariff_prices):
        history = []
        self.price_data = tariff_prices['current']
        current = self.tariff_format if self.price_data else {}

        for tariff_price in tariff_prices['history']:
            if tariff_price:
                self.price_data = tariff_price
                history.append(self.tariff_format)
        return current, history

    @property
    def tariff(self):
        tariff_prices = self.get_erp_tariff_prices
        if "error" in tariff_prices.keys():
            return {"error": tariff_prices.get("error", False), "tariffPriceId": self.tariff_id}
        if tariff_prices:
            if self.contract_id:
                contract_tariff_prices = {"history": []}
                for tariff_id, tariff_price in tariff_prices.items():
                    current, history = self.to_tariff_format(tariff_price)
                    if current != {}:
                        contract_tariff_prices['current'] = {
                            "tariffPriceId": tariff_id,
                            "prices": current,
                        }
                    contract_tariff_prices['history'].append(
                        {
                            "tariffPriceId": tariff_id,
                            "prices": history,
                        })
                return contract_tariff_prices
            else:
                current, history = self.to_tariff_format(tariff_prices)
                return {
                    "tariffPriceId": self.tariff_id,
                    "prices":{
                        "current": current,
                        "history": history
                    }
                }

    def __iter__(self):
        if not 'error' in self.tariff.keys():
            yield from self.tariff.items()


def get_tariff_filters(request, contract_id=None):
    BOOL_TABLE = {
        'true': True,
        'false': False
    }

    filters = dict(request.query_args)

    filters['withTaxes'] = BOOL_TABLE.get(filters.get('withTaxes', '').lower(), False)
    filters['home'] = BOOL_TABLE.get(filters.get('home', '').lower(), False)

    if contract_id:
        filters["contract_id"] = contract_id
        return filters
    return filters

def get_tariffs(request):
    tariff_obj = request.app.ctx.erp_client.model("giscedata.polissa.tarifa")
    erp_filters = [
        ("active", "=", True),
    ]
    filters = dict(request.query_args)

    if "tariffPriceId" in filters:
        return request.args["tariffPriceId"]

    if "type" in filters:
        erp_filters += [
            ("name", "=", request.args["type"][0]),
        ]
        tariff_id = tariff_obj.search(erp_filters)
        return tariff_id

    tariff_ids = tariff_obj.search(erp_filters)
    return tariff_ids


async def async_get_tariff_prices(request, contract_id = None):
    try:
        tariff = await request.app.loop.run_in_executor(
            None,
            functools.partial(get_tariffs, request),
        )
    except Exception as e:
        raise e
    return tariff
