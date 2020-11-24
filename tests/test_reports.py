
import asyncio
from passlib.hash import pbkdf2_sha256
from pony.orm import db_session
import json as jsonlib
from motor.motor_asyncio import AsyncIOMotorClient
from tests.base import BaseTestCase

from infoenergia_api.contrib import beedataApi, process_report, save_report, read_report


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
              'contract_ids': ['0000004', '0000010'],
              'type': "infoenergia"
            },
            timeout=None
        )

        self.assertEqual(response.status, 200)
        self.assertEqual(jsonlib.loads(response.body), ['0000004', '0000010'])
        self.delete_user(user)

    def test__login_to_beedata(self):

        bapi = beedataApi()
        status = self.loop.run_until_complete(bapi.login())

        self.assertEqual(status, 200)
        self.assertNotEqual(bapi.token, None)

    def test__download_reports(self):
        bapi = beedataApi()
        status = self.loop.run_until_complete(bapi.login())

        status, response = self.loop.run_until_complete(
            bapi.download_reports(
                contractId="0090438"
            )
        )
        self.assertEqual(status, 200)
        # TODO check report correctly downloaded o algo

    # TODO cleanup after test mock fake session...
    def test__insert_report(self):

        report = {'test': 'report'}
        reportId = self.loop.run_until_complete(
            save_report(report)
        )
        expectedReport = self.loop.run_until_complete(
            read_report(reportId)
        )

        self.assertDictEqual(report, expectedReport)
