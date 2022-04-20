
import unittest
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

from infoenergia_api.contrib import Beedata, BeedataApiClient, get_report_ids

class TestReport(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.app.redis = fakeredis.FakeStrictRedis()
        self.app.mongo_client = AsyncIOMotorClient(self.app.config.MONGO_CONF)
        self.loop = asyncio.get_event_loop()
        self.bapi = asyncio.run(BeedataApiClient.create(
            url=self.app.config.BASE_URL,
            username=self.app.config.USERNAME,
            password=self.app.config.PASSWORD,
            company_id=self.app.config.COMPANY_ID,
            cert_file=self.app.config.CERT_FILE,
            cert_key=self.app.config.KEY_FILE
        ))

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
              'contract_ids': ["0180471", "0010012", "1000010"],
              'type': 'CCH',
              'create_at': "2020-01-01",
              'month': '202011'
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'reports': 3,
            }
        )

        self.delete_user(user)

    @db_session
    def test__post_photovoltaic_contracts(self):
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
              'contract_ids': ["0068759", "0010012", "1000010"],
              'type': "photovoltaic_reports",
              'create_at': "2020-01-01",
              'month': '202011'
            },
            timeout=None
        )
        self.assertEqual(response.status, 200)
        self.assertDictEqual(
            response.json,
            {
                'reports': 3,
            }
        )
        self.delete_user(user)

    def test__login_to_beedata(self):
        bapi = Beedata(self.bapi, self.app.mongo_client, self.app.redis)
        status = asyncio.run(
            bapi.api_client.login(self.app.config.USERNAME, self.app.config.PASSWORD)
        )

        self.assertNotEqual(status.token, None)



class TestBaseReportsAsync(BaseTestCaseAsync):

    def setUp(self):
        super().setUp()
        self.app.redis = fakeredis.FakeStrictRedis()
        self.app.mongo_client = AsyncIOMotorClient(self.app.config.MONGO_CONF)
        bapi_client = asyncio.run(BeedataApiClient.create(
            url=self.app.config.BASE_URL,
            username=self.app.config.USERNAME,
            password=self.app.config.PASSWORD,
            company_id=self.app.config.COMPANY_ID,
            cert_file=self.app.config.CERT_FILE,
            cert_key=self.app.config.KEY_FILE
        ))
        self.bapi = Beedata(bapi_client, self.app.mongo_client, self.app.redis)

    @unittest_run_loop
    async def test__download_one_report(self):
        async with aiohttp.ClientSession() as session:
            status, report = await self.bapi.api_client.download_report(
                contract_id="0090438",
                month='202011',
                report_type='CCH'
            )
        self.assertEqual(status, 200)
        self.assertIsNotNone(report)
        # TODO check report correctly downloaded

    @unittest_run_loop
    async def test__download_one_report__wrongid(self):
        async with aiohttp.ClientSession() as session:
            status, report = await self.bapi.api_client.download_report(
                contract_id="1090438",
                month='202011',
                report_type='CCH'
            )
        self.assertEqual(status, 200)
        self.assertIsNone(report)

    @db_session
    @unittest_run_loop
    async def test__process_one_valid_report(self):
        self.bapi.save_report = mock.AsyncMock(return_value='1234')
        async with aiohttp.ClientSession() as session:
            result = await self.bapi.process_one_report(
                month='202011',
                report_type='CCH',
                contract_id=b'0090438'
            )
        self.assertTrue(result)

    @db_session
    @unittest_run_loop
    async def test__process_one_invalid_report(self):
        self.bapi.save_report = mock.AsyncMock(return_value='')

        async with aiohttp.ClientSession() as session:
            result = await self.bapi.process_one_report(
                month='202011',
                report_type='CCH',
                contract_id=b"0090438"
            )
        self.assertFalse(result)

    @db_session
    @unittest_run_loop
    async def test__insert_or_update_report(self):
        report_type = 'infoenergia_reports'
        report = [{
            'contractId': '1234567',
            '_updated': "2020-08-18T12:06:23Z",
            '_created':  "2020-08-18T12:06:23Z",
            'month': '202009',
            'type': 'CCH',
            'results': {},
        }]
        reportId = await self.bapi.save_report(report, report_type)
        expectedReport = await self.app.mongo_client.somenergia.infoenergia_reports.find_one(reportId[0])
        self.assertEqual(reportId[0], expectedReport['_id'])

    @unittest_run_loop
    async def test__download_one_report__expected_infoenergia_fields(self):
        async with aiohttp.ClientSession() as session:
            status, report = await self.bapi.api_client.download_report(
                contract_id="0068759",
                month='202011',
                report_type='infoenergia_reports'
            )
        self.assertEqual(status, 200)
        self.assertIsNotNone(report)
        self.assertTrue('seasonalProfile' in report[0]['results'])

    @unittest_run_loop
    async def test__download_one_report__expected_photovoltaic_fields(self):
        async with aiohttp.ClientSession() as session:
            status, report = await self.bapi.api_client.download_report(
                contract_id="0068759",
                month=None,
                report_type='photovoltaic_reports'
            )
        self.assertEqual(status, 200)
        self.assertIsNotNone(report)
        self.assertTrue('pvAutoSize' in report[0]['results'])
