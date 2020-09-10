from passlib.hash import pbkdf2_sha256
from pony.orm import db_session

from tests.base import BaseTestCase

from infoenergia_api.contrib import F5D




class TestF5D(BaseTestCase):

    contract_id = 4
    contract_id_cch = 132850
    contract_id_3X = 158697

    f5d_id = 1806168064

    def test__create_f5d(self):
        f5d = F5D(self.f5d_id)

        self.assertIsInstance(f5d, F5D)

    def test__get_measurements(self):
        f5d = F5D(self.f5d_id)
        metering_point = f5d.measurements
        self.assertDictEqual(
            metering_point,
            {
                'ai': 443,
                'ao': 0,
                'date': '2017-11-16 03:00:00+0000',
                'dateDownload': '2017-12-28 03:49:21',
                'dateUpdate': '2017-12-28 03:49:21',
                'r1': 41,
                'r2': 0,
                'r3': 0,
                'r4': 21,
                'season': 0,
                'source': 1,
                'validated': True
            })
