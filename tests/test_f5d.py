from unittest import mock

from passlib.hash import pbkdf2_sha256
from pony.orm import db_session

from tests.base import BaseTestCase

from infoenergia_api.contrib import F5D


class TestBaseF5D(BaseTestCase):

    @mock.patch('infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor')
    @db_session
    def test__get_f5d_by_id__2A(self, next_cursor_mock):
        next_cursor_mock.return_value = 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0='

        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2018-11-16',
            'to_': '2018-12-16'
        }
        _, response = self.client.get(
            '/f5d/' + self.json4test['f5d']['contractId'],
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 50,
                'cursor': 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=',
                'next_page':'http://{}/f5d/0067411?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=50'.format(response.url.authority),
                'data': self.json4test['f5d']['cch_data'],
            }
        )
        self.delete_user(user)


    @mock.patch('infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor')
    @db_session
    def test__get_f5d__all_contracts(self, next_cursor_mock):
        next_cursor_mock.return_value = 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0='

        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2019-10-03',
            'to_': '2019-10-09',
        }
        _, response = self.client.get(
            '/f5d',
            params=params,
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'count': 50,
                'cursor': 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=',
                'next_page':'http://{}/f5d?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=50'.format(response.url.authority),
                'data': self.json4test['f5d_all']['cch_data'],
            }
        )
        self.delete_user(user)


class TestF5D(BaseTestCase):

    f5d_id_empty = 4
    f5d_id = 1806168064

    def test__create_f5d(self):
        f5d = F5D(self.f5d_id)
        self.assertIsInstance(f5d, F5D)


    def test__get_measurements(self):
        f5d = F5D(self.f5d_id)
        data = f5d.measurements
        self.assertDictEqual(
            data,
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

    def test__valid_empowering(self):
        f5d = F5D(self.f5d_id)
        valid = f5d.is_valid_empowering
        self.assertEqual(True, valid)
