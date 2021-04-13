import asyncio
from unittest import mock

from aiohttp.test_utils import unittest_run_loop
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
            'limit':10,
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
                'count': 10,
                'total_results': 721,
                'cursor': 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=',
                'next_page':'http://{}/cch/0067411?type=tg_cchfact&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=10'.format(response.url.netloc),
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
            'to_': '2019-10-08',
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
                'total_results': 114333,
                'cursor': 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=',
                'next_page':'http://{}/cch?type=tg_cchfact&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=50'.format(response.url.netloc),
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
                'count': 24,
                'total_results': 24,
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
        self.f1_id = '5e1d8d9612cd738e89bb3cfb'

    @unittest_run_loop
    async def test__create_f5d(self):
        f5d = await Cch.create(self.f5d_id, 'tg_cchfact')
        self.assertIsInstance(f5d, Cch)

    @unittest_run_loop
    async def test__get_f5d_measurements(self):
        f5d = await Cch.create(self.f5d_id, 'tg_cchfact')
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

    @unittest_run_loop
    async def test__create_f1(self):
        f1 = await Cch.create(self.f1_id, 'tg_f1')
        self.assertIsInstance(f1, Cch)

    @unittest_run_loop
    async def test__get_f1_measurements(self):
        f1 = await Cch.create(self.f1_id, 'tg_f1')
        data = f1.measurements
        self.assertDictEqual(
            data,
            {
                'ai': 14.0,
                'ao': 0.0,
                'date': '2017-12-01 22:00:00+0000',
                'dateUpdate': '2020-01-14 10:44:54',
                'season': 0,
                'validated': False,
                'r1': 1.0,
                'r2': 0.0,
                'r3': 0.0,
                'r4': 2.0,
                'reserve1': 0,
                'reserve2': 0,
                'source': 1,
                'measureType': 11,
                'dateDownload': '2020-01-14 10:44:54'
            }
        )