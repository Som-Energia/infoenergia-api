
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
              'type': "infoenergia",
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
    @unittest.skip("waiting for Beedata endpoint implementation")
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
              'contract_ids': ["0180471", "0010012", "1000010"],
              'type': "photovoltaic",
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


class TestBaseReportsAsync(BaseTestCaseAsync):

    def setUp(self):
        super().setUp()
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
                report_type='infoenergia'
            )
        self.assertEqual(status, 200)
        self.assertIsNotNone(report)
        # TODO check report correctly downloaded

    @unittest_run_loop
    async def test__download_one_report__wrongid(self):
        async with aiohttp.ClientSession() as session:
            status, report = await self.bapi.api_client.download_report(
                contract_id='2090438',
                month='202011',
                report_type='infoenergia'
            )
        self.assertEqual(status, 200)
        self.assertIsNone(report)

    @mock.patch('infoenergia_api.contrib.reports.Beedata.save_report')
    @db_session
    @unittest_run_loop
    async def test__process_one_valid_report(self, saved_report_mock):
        saved_report_mock.return_value = '1234'

        async with aiohttp.ClientSession() as session:
            result = await self.bapi.process_one_report(
                month='202011',
                report_type='infoenergia',
                contract_id=b"0090438"
            )
        self.assertTrue(result)

    @mock.patch('infoenergia_api.contrib.reports.Beedata.save_report')
    @db_session
    @unittest_run_loop
    async def test__process_one_invalid_report(self, saved_report_mock):
        saved_report_mock.return_value = ''

        async with aiohttp.ClientSession() as session:
            result = await self.bapi.process_one_report(
                month='202011',
                report_type='infoenergia',
                contract_id=b"0090438",
            )
        self.assertFalse(result)

    @db_session
    @unittest_run_loop
    async def test__insert_or_update_report(self):
        report = [{
            'contractId': '1234567',
            '_updated': "2020-08-18T12:06:23Z",
            '_created':  "2020-08-18T12:06:23Z",
            'month': '202009',
            'results': {},
        }]
        reportId = await self.bapi.save_report(report)
        expectedReport = await self.app.mongo_client.somenergia.infoenergia_reports.find_one(reportId[0])
        self.assertEqual(reportId[0], expectedReport['_id'])
