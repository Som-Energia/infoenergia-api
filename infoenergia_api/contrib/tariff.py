

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
            #[('id', '=', price_id), ('type', '=', 'sale')],
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
        return {
            'tariff': self.name,
            'tariffId': self.id,
            'price': self.price,
        }
