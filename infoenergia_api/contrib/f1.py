import functools
import re
from sanic.request import RequestParameters

from infoenergia_api.utils import (get_request_filters, make_utc_timestamp,
                                   make_uuid, get_invoice_user_filters)


class Invoice(object):

    FIELDS = [
        'polissa_id',
        'data_inici',
        'data_final',
        'cups_id',
        'comptadors',
        'lectures_potencia_ids',
        'lectures_energia_ids',
        'tarifa_acces_id',
        'maximetre_consumidor_ids'
    ]

    def __init__(self, invoice_id):
        from infoenergia_api.app import app

        self._erp = app.erp_client
        self._FacturacioFactura = self._erp.model('giscedata.facturacio.factura')
        for name, value in self._FacturacioFactura.read(invoice_id, self.FIELDS).items():
            setattr(self, name, value)

    @property
    def devices(self):
        """
        All devices:
        [
          {
            'dateStart': '2019-10-03T00:00:00-00:15Z',
            'dateEnd': None,
            'deviceId': 'ee3f4996-788e-59b3-9530-0e02d99b45b7'
          }
        ]
        """
        if not self.comptadors:
            return []

        compt_obj = self._erp.model('giscedata.lectures.comptador')
        fields = ['data_alta', 'data_baixa']

        devices = []
        for comptador in compt_obj.read(self.comptadors, fields) or []:
            devices.append(
                {
                    'dateStart': make_utc_timestamp(comptador['data_alta']),
                    'dateEnd': make_utc_timestamp(comptador['data_baixa']),
                    'deviceId': make_uuid(
                        'giscedata.lectures.comptador',
                        comptador['id']
                    )
                }
            )
        return devices

    @property
    def f1_power_kW(self):
        """
        Readings F1:
        "power_measurements": {
          "period": "P1",
          "excess": "0.0",
          "maximeter": "2",
          "units": "kW"
        }
        """

        power_obj = self._erp.model('giscedata.facturacio.lectures.potencia')
        f1_power = power_obj.read([('id', 'in', self.lectures_potencia_ids)])
        return [{
            'period': power['name'],
            'excess': power['exces'],
            'maximeter': power['pot_maximetre'],
            'units': 'kW'
            } for power in f1_power
        ]

    @property
    def f1_reactive_energy_kVArh(self):
        """
        Readings F1:
        "energy_measurements": {
          "energyType": activa/reactiva
          "source": telegestión/real
          "period": "P1",
          "consum": "2",
          "units": "kVArh"
        }
        """
        measures_obj = self._erp.model('giscedata.facturacio.lectures.energia')
        measures = measures_obj.read([('id', 'in', self.lectures_energia_ids)])
        return [{
            'source': measure.get('origen_id') and measure['origen_id'][1] or 'Not informed',
            'period': re.split('[()]', measure['name'])[1],
            'consum': int(measure['consum']),
            'units': 'kVArh'
        } for measure in measures if measure['tipus'] == 'reactiva']

    @property
    def f1_active_energy_kWh(self):
        """
        Readings F1:
        "energy_measurements": {
          "energyType": activa/reactiva
          "source": telegestión/real
          "period": "P1",
          "consum": "2",
          "units": "kWh"
        }
        """
        measures_obj = self._erp.model('giscedata.facturacio.lectures.energia')
        measures = measures_obj.read(
            [('id', 'in', sorted(self.lectures_energia_ids))],
        )
        return [{
            'source': measure.get('origen_id') and measure['origen_id'][1] or 'Not informed',
            'period': re.split('[()]', measure['name'])[1],
            'consum': int(measure['consum']),
            'units': 'kWh'
        } for measure in measures if measure['tipus'] == 'activa']

    @property
    def f1_maximeter(self):
        """
        f1_maximeter: {
            'dateStart': 2021-06-01,
            'dateEnd': 2021-09-10,
            'maxPower': 4.95,
            'period': '2.0TD (P2)'
        """
        maximeter_obj=self._erp.model('giscedata.f1.maximetre.consumidor')
        maximeters = maximeter_obj.read(self.maximetre_consumidor_ids)

        return[{
            'dateStart':maximeter['data_inici'],
            'dateEnd':maximeter['data_final'],
            'maxPower':maximeter['maximetre'],
            'period':maximeter['periode_id'][1]
        } for maximeter in maximeters]


    @property
    def f1_measures(self):
        return {
            'contractId': self.polissa_id[1],
            'invoiceId': make_uuid('giscedata.facturacio.factura', self.id),
            'dateStart': make_utc_timestamp(self.data_inici),
            'dateEnd': make_utc_timestamp(self.data_final),
            'tariffId': self.tarifa_acces_id[1],
            'meteringPointId': make_uuid('giscedata.cups.ps',self.cups_id[1]),
            'devices': self.devices,
            'power_measurements': self.f1_power_kW,
            'reactive_energy_measurements': self.f1_reactive_energy_kVArh,
            'active_energy_measurements': self.f1_active_energy_kWh,
            'maximeter': self.f1_maximeter
        }


def get_invoices(request, contractId=None):
    args = RequestParameters(request.args)
    factura_obj = request.app.erp_client.model('giscedata.facturacio.factura')
    filters = [
        ('polissa_state', '=', 'activa'),
        ('type', '=', 'in_invoice'),
        ('polissa_id.emp_allow_send_data', '=', True),
    ]
    filters = get_invoice_user_filters(
        request.app.erp_client, request.ctx.user, filters
    )

    if contractId:
        filters.append(
            ('polissa_id.name', '=', contractId)
        )

    if args:
        filters = get_request_filters(
            request.app.erp_client,
            request,
            filters,
        )

    invoices_ids = factura_obj.search(filters)
    return invoices_ids


async def async_get_invoices(request, id_contract=None):
    try:
        invoices = await request.app.loop.run_in_executor(
            request.app.thread_pool,
            functools.partial(get_invoices, request, id_contract)
        )
    except Exception as e:
        raise e

    return invoices
