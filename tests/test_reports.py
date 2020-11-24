from passlib.hash import pbkdf2_sha256
from pony.orm import db_session
import json as jsonlib
import asyncio

from tests.base import BaseTestCase

from infoenergia_api.contrib import beedataApi, process_report


class TestBaseReports(BaseTestCase):

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

        loop = asyncio.get_event_loop()

        bapi = beedataApi()

        status = loop.run_until_complete(bapi.login())

        self.assertEqual(status, 200)
        self.assertNotEqual(bapi.token, None)


    def test__download_reports(self):
        login_url = "https://api.beedataanalytics.com/authn/login"

        username = "test@test"
        password = "test1234"

        bapi = beedataApi()

        loop = asyncio.get_event_loop()

        status = loop.run_until_complete(bapi.login())

        status, response = loop.run_until_complete(
            bapi.download_reports(
                contractId="0090438"
            )
        )
        self.assertEqual(status, 200)
        # TODO check report correctly downloaded o algo
