import asyncio
from unittest import mock

from motor.motor_asyncio import AsyncIOMotorClient
from pony.orm import db_session

from tests.base import BaseTestCase
from infoenergia_api.contrib import Cch


class TestBaseCch(BaseTestCase):

    @mock.patch('infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor')
    @db_session
    def test__get_f5d_by_id__2A(self, next_cursor_mock):
        next_cursor_mock.return_value = 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0='

        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2018-11-16',
            'to_': '2018-12-16',
            'type': 'tg_cchfact'
        }
        _, response = self.client.get(
            '/cch/' + self.json4test['f5d']['contractId'],
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
                'total_results': 719,
                'cursor': 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=',
                'next_page':'http://{}/cch/0067411?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=50'.format(response.url.netloc),
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
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'to_': '2019-10-09',
            'type': 'tg_cchfact'
        }
        _, response = self.client.get(
            '/cch',
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
                'total_results': 22796,
                'cursor': 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=',
                'next_page':'http://{}/cch?cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=50'.format(response.url.netloc),
                'data': self.json4test['f5d_all']['cch_data'],
            }
        )
        self.delete_user(user)


    @db_session
    def test__get_f5d_without_permission(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=False,
            category='Energética'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2018-11-16',
            'to_': '2018-12-16',
            'type': 'tg_cchfact'
        }
        _, response = self.client.get(
            '/cch/' + self.json4test['f5d']['contractId'],
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
                'count': 0,
                'total_results': 0,
                'data': []
            }
        )
        self.delete_user(user)

    @mock.patch('infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor')
    @db_session
    def test__get_p5d__for_contract_id(self, next_cursor_mock):
        next_cursor_mock.return_value = 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0='

        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'from_': '2017-12-29',
            'to_': '2018-01-01',
            'type': 'tg_cchval'
        }
        _, response = self.client.get(
            '/cch/' + self.json4test['p5d']['contractId'],
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
                'count': 23,
                'total_results': 23,
                'data': self.json4test['p5d']['cch_data'],
            }
        )
        self.delete_user(user)


    @db_session
    def test__get_p5d_without_permission(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=False,
            category='Energética'
        )
        token = self.get_auth_token(user.username, "123412345")
        params = {
            'type': 'tg_cchval'
        }
        _, response = self.client.get(
            '/cch/' + self.json4test['p5d']['contractId'],
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
                'count': 0,
                'total_results': 0,
                'data': []
            }
        )
        self.delete_user(user)

class TestCch(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.app.mongo_client = AsyncIOMotorClient(self.app.config.MONGO_CONF)
        self.loop = asyncio.get_event_loop()
        self.f5d_id = '5c2dd783cb2f477212c77abb'

    def test__create_f5d(self):
        f5d = self.loop.run_until_complete(Cch.create(self.f5d_id, 'tg_cchfact'))
        self.assertIsInstance(f5d, Cch)

    def test__get_measurements(self):
        f5d = self.loop.run_until_complete(Cch.create(self.f5d_id, 'tg_cchfact'))
        data = f5d.measurements
        self.assertDictEqual(
            data,
            {
                'ai': 496,
                'ao': 0,
                'date': '2018-11-15 23:00:00+0000',
                'dateDownload': '2019-01-03 10:36:03',
                'dateUpdate': '2019-01-03 16:56:28',
                'r1': 134,
                'r2': 0,
                'r3': 0,
                'r4': 0,
                'season': 0,
                'source': 1,
                'validated': True
            })
