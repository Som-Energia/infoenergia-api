
import aiohttp
import asyncio
import json as jsonlib
import fakeredis

from aiohttp.test_utils import unittest_run_loop
from passlib.hash import pbkdf2_sha256
from pony.orm import db_session
from motor.motor_asyncio import AsyncIOMotorClient
from tests.base import BaseTestCase, BaseTestCaseAsync
from unittest import mock

from infoenergia_api.contrib import beedataApi, get_report_ids
from infoenergia_api.utils import read_report, save_report

class TestReport(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.app.redis = fakeredis.FakeStrictRedis()
        self.app.mongo_client = AsyncIOMotorClient(self.app.config.MONGO_CONF)
        self.loop = asyncio.get_event_loop()

    @db_session
    def test__post_contracts(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        token = self.get_auth_token(user.username, "123412345")
        _, response = self.client.post(
            '/reports/',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            },
            json={
              'id': "summer_2020",
              'contract_ids': ['0090438', '0000010', '0000004'],
              'type': "infoenergia",
              'create_at': "2020-01-01",
              'month': '202010'
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'reports': 3,
                'unprocessed_reports':['0000010', '0000004'],
            }
        )
        self.delete_user(user)

    def test__login_to_beedata(self):
        bapi = beedataApi()
        status = self.loop.run_until_complete(bapi.login())

        self.assertEqual(status, 200)
        self.assertNotEqual(bapi.token, None)


class TestBaseReportsAsync(BaseTestCaseAsync):

    @unittest_run_loop
    async def test__download_one_report(self):
        bapi = beedataApi()

        status = await bapi.login()
        headers = {
          'X-CompanyId': str(bapi.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(bapi.token)
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            status, report = await bapi.download_one_report(
                    session,
                    contractId="0090438"
                )
        self.assertEqual(status, 200)
        self.assertIsNotNone(report)
        # TODO check report correctly downloaded

    @unittest_run_loop
    async def test__download_one_report__wrongid(self):

        bapi = beedataApi()
        status = await bapi.login()

        headers = {
          'X-CompanyId': str(bapi.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(bapi.token)
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            status, report = await bapi.download_one_report(
                    session,
                    contractId="1090438"
                )
        self.assertEqual(status, 200)
        self.assertIsNone(report)

    @mock.patch('infoenergia_api.contrib.reports.save_report')
    @db_session
    @unittest_run_loop
    async def test__process_one_valid_report(self, saved_report_mock):
        saved_report_mock.return_value = '1234'

        bapi = beedataApi()
        status = await bapi.login()

        headers = {
          'X-CompanyId': str(bapi.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(bapi.token)
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            result = await bapi.process_one_report(
                    session,
                    contractId=b"0090438"
                )
        self.assertEqual(status, 200)
        self.assertTrue(result)

    @mock.patch('infoenergia_api.contrib.reports.save_report')
    @db_session
    @unittest_run_loop
    async def test__process_one_invalid_report(self, saved_report_mock):
        saved_report_mock.return_value = ''

        bapi = beedataApi()
        status = await bapi.login()

        headers = {
          'X-CompanyId': str(bapi.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(bapi.token)
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            result = await bapi.process_one_report(
                    session,
                    contractId=b"0090438"
                )
        self.assertEqual(status, 200)
        self.assertFalse(result)
