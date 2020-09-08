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
         'name': P1-ENERGIA-20A_SOM
         'period': P1
         'price': 0.139
         'units': €/kWh
         }]
        """
        fields = [
            'product_id',
            'name',
            'price_surcharge',
            'price_version_id'
        ]
        priceitem_obj = self._erp.model('product.pricelist.item')
        term_price = priceitem_obj.read(items_id, fields)

        return [{
            'name': tp['name'],
            'period': tp['name'].split('_')[0],
            'price': tp['price_surcharge'],
            'units': units
            } for tp in term_price
            if tp['name'].find(term_type) > 0
        ]

    def reactiveEnergyPrice(self, price_version_id, name):
        priceitem_obj = self._erp.model('product.pricelist.item')

        return priceitem_obj.read(
            [
                ('name', 'like', '%Cos%'),
                ('base_pricelist_id', '=', 3),
                ('price_version_id', '=', price_version_id),
                ('name', '=', name),
            ]
        )[0]['price_surcharge']


    @property
    def reactiveEnergy(self):
        fields = [
            'product_id',
            'name',
            'price_surcharge',
            'price_version_id'
        ]
        priceitem_obj = self._erp.model('product.pricelist.item')
        reactive_price = priceitem_obj.read(
            [
                ('name', 'like', '%Cos%'),
                ('base_pricelist_id', '=', 3),
            ], fields , order='price_version_id'
        )
        return [{
                'BOE': rp.get('price_version_id')[1],
                'price33': self.reactiveEnergyPrice(rp['price_version_id'][0], str('Cos(fi) 0.80 - 0.95')),
                'price75': self.reactiveEnergyPrice(rp['price_version_id'][0], str('Cos(fi) 0 - 0.80')),
                'units': '€/kVArh'
                } for rp in reactive_price
            ] or []


    @property
    def priceDetail(self):
        """
        Tariff prices
         2020-06-01
        """
        fields = [
            'date_start',
            'date_end',
            'items_id',
            'id',
            'name',
        ]
        priceversion_obj = self._erp.model('product.pricelist.version')
        prices = priceversion_obj.read(self.version_id, fields)
        return [{
            'dateStart': price['date_start'],
            'dateEnd': price['date_end'],
            'activeEnergy': self.termPrice(price['items_id'], 'ENERGIA', '€/kWh'),
            'power': self.termPrice(price['items_id'], 'POTENCIA', '€/kW year'),
            'GKWh': self.termPrice(price['items_id'], 'GKWh', '€/kWh'),
            } for price in prices]

    @property
    def tariff(self):
        return {
            'tariffId': self.id,
            'price': self.priceDetail[0],
            'priceReactiveEnergy': self.reactiveEnergy[-1],
            'priceHistory': self.priceDetail,
            'priceReactiveEnergyHistory': self.reactiveEnergy
        }

def get_tariff_prices(request, contractId=None):
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
    if contractId:
        tariffId =contract_obj.read(
            [('name', '=', contractId)],
            ['tarifa']
        )[0]['tarifa'][1]
        filters.append(('name', '=', tariffId))
    tariff_id = tariff_obj.search(filters)
    tariff_price_ids = tariff_obj.read(tariff_id)[0]['llistes_preus_comptatibles']

    return tariff_price_ids


async def async_get_tariff_prices(request, contractId=None):
    try:
        tariff = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_tariff_prices, request, contractId)
        )
    except Exception as e:
        raise e
    return tariff
