import functools
from sanic.log import logger

from ..utils import (get_request_filters, make_uuid)

class Tariff(object):
    FIELDS = [
        'id',
        'name',
        'version_id',
        'type'
    ]

    def __init__(self, price_id):
        from infoenergia_api.app import app

        self._erp = app.erp_client
        self._Pricelist = self._erp.model('product.pricelist')
        for name, value in self._Pricelist.read(price_id,
             self.FIELDS).items():
            setattr(self, name, value)


    def termPrice(self, items_id, term_type, units):
        """
        Term price
         [{
         'name': P1-POTENCIA-20A_SOM
         'period': P1
         'price': 0.12
         'units': kWh/year
         }]
        """
        fields = [
            'product_id',
            'name',
            'price_surcharge',
        ]
        priceitem_obj = self._erp.model('product.pricelist.item')
        term_price = priceitem_obj.read(items_id, fields)
        return [{
            'name': ep['name'],
            'period': ep['name'].split('_')[0],
            'price': ep['price_surcharge'],
            'units': units
            } for ep in term_price
            if ep['name'].find(term_type) > 0
        ]

    @property
    def priceDetail(self):
        """
        Tariff prices
         2020-06-01
        """
        fields = [
            'date_start',
            'date_end',
            'items_id'
        ]
        priceversion_obj = self._erp.model('product.pricelist.version')
        prices = priceversion_obj.read(self.version_id, fields)

        return [{
            'dateStart': price['date_start'],
            'dateEnd': price['date_end'],
            'activeEnergy': self.termPrice(price['items_id'], 'ENERGIA', 'kWh/day'),
            'reactiveEnergy': self.termPrice(price['items_id'], 'REACTIVA', 'kWh/day'),
            'power': self.termPrice(price['items_id'], 'POTENCIA', 'kW/year'),
            'GKWh': self.termPrice(price['items_id'], 'GKWh', 'kWh/day'),
            } for price in prices]

    @property
    def tariff(self):
        if self.type == 'sale':
            return {
                'tariffId': self.id,
                'price': self.priceDetail[-1],
                'priceHistory': self.priceDetail,
            }

def get_tariff_prices(request):
    tariff_obj = request.app.erp_client.model('giscedata.polissa.tarifa')
    contract_obj = request.app.erp_client.model('giscedata.polissa')
    filters = [
        ('active', '=', True),
    ]

    if request.args:
        filters = get_request_filters(
            request.app.erp_client,
            request,
            filters,
        )

async def async_get_tariff_prices(request):
    try:
        tariff = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_tariff_prices, request)
        )
    except Exception as e:
        raise e
    return tariff
