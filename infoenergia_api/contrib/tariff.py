

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

    def term(self, items_id, energy_type, units):
        """
        Term price
         [{
         'name':
         'period':
         'price':
         'units':
         }]
        """
        fields = [
            'product_id',
            'name',
            'price_surcharge',
        ]
        priceitem_obj = self._erp.model('product.pricelist.item')
        energy_price = priceitem_obj.read(items_id, fields)
        print(energy_price)
        return [{
            'name': ep['name'],
            'period': ep['name'].split('_')[0],
            'price': ep['price_surcharge'],
            'units': units
            } for ep in energy_price
            if ep['product_id']
            if ep['name'].split('_')[1].casefold() == energy_type
        ]

    @property
    def price(self):
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
            'activeEnergy': self.term(price['items_id'], 'energia', 'kWh/day'),
            'reactiveEnergy': self.term(price['items_id'], 'reactiva', 'kWh/day'),
            'power': self.term(price['items_id'], 'potencia', 'kW/year'),
            'GkWh': self.term(price['items_id'], 'GKWh', 'kWh')
            } for price in prices]

    @property
    def tariff(self):
        return {
            'tariff': self.name,
            'tariffId': self.id,
            'price': self.price,
        }
