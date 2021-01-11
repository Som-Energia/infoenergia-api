
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
        self.app.mongo_client = AsyncIOMotorClient(self.app.config.MONGO_CONF)
        self.loop = asyncio.get_event_loop()

    def _test_download_reports(self):
        bapi = beedataApi()
        contractId = "0090438"

        status = self.loop.run_until_complete(bapi.login())
        headers = {
          'X-CompanyId': str(bapi.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(bapi.token)
        }
        expectedReport = self.loop.run_until_complete(
            read_report(reportId)
        )

        self.assertDictEqual(reportId, expectedReport)

    def _test__get_report_ids(self):
        bapi = beedataApi()
        contractIdsList = ["0090438", "0000004", "0000010"]

        status = self.loop.run_until_complete(bapi.login())

        results = self.loop.run_until_complete(
            get_report_ids()
        )
        print(results)
        self.assertListEqual(results, contractIdsList)

    def test__process_reports(self):
        bapi = beedataApi()
        contractIdsList = ["0090438", "0000004", "0000010"]

        self.loop.run_until_complete(bapi.login())

        status = self.loop.run_until_complete(
            bapi.process_reports(contractIdsList)
        )

        self.assertEqual(status, 200)

    def test__process_reports__one_report(self):
        bapi = beedataApi()
        contractIdsList = ["0000010"]

        self.loop.run_until_complete(bapi.login())

        status = self.loop.run_until_complete(
            bapi.process_reports(contractIdsList)
        )

        self.assertEqual(status, 200)

    def test__process_reports__wrong_id(self):
        bapi = beedataApi()
        contractIdsList = ["1000010"]

        self.loop.run_until_complete(bapi.login())

        status = self.loop.run_until_complete(
            bapi.process_reports(contractIdsList)
        )

        self.assertEqual(status, 200)

    def _test__process_reports__mixed_results(self):
        bapi = beedataApi()
        contractIdsList = ["0090438", "1000010"]

        self.loop.run_until_complete(bapi.login())

        status = self.loop.run_until_complete(
            bapi.process_reports(contractIdsList)
        )

        self.assertEqual(status, 200)


class TestBaseReports(BaseTestCase):

    def setUp(self):
        super().setUp()
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
        self.delete_user(user)

    def test__login_to_beedata(self):

        bapi = beedataApi()
        status = self.loop.run_until_complete(bapi.login())

        self.assertEqual(status, 200)
        self.assertNotEqual(bapi.token, None)

    # TODO cleanup after test mock fake session...
    def _test__insert_report(self):

        report = {'test': 'report'}
        reportId = self.loop.run_until_complete(
            save_report(report)
        )
        expectedReport = self.loop.run_until_complete(
            read_report(reportId)
        )

        self.assertDictEqual(report, expectedReport)

    def _test__download_two_reports(self):
        bapi = beedataApi()
        status = self.loop.run_until_complete(bapi.login())
        status, response = self.loop.run_until_complete(
            bapi.download_reports(
                contractId=["0090438", "0000004"]
            )
        )
        self.assertEqual(status, 200)


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
        # TODO check report correctly downloaded o algo

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
