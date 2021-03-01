import asyncio
import os

import aiohttp
import vcr

from infoenergia_api.contrib import ApiException, BeedataApiClient
from tests.base import BaseTestCase

class TestBeedataApiClient(BaseTestCase):

    @property
    def beedata_api_correct_credentials(self):
        return dict(
            url=os.environ.get('BASE_URL'),
            username=os.environ.get('USERNAME'),
            password=os.environ.get('PASSWORD'),
            company_id=os.environ.get('COMPANY_ID'),
            cert_file=os.environ.get('CERT_FILE'),
            cert_key=os.environ.get('KEY_FILE')
        )
    
    @property
    def beedata_api_bad_credentials(self):
        return dict(
            url=os.environ.get('BASE_URL'),
            username='erdtfy1253',
            password=os.environ.get('PASSWORD'),
            company_id=os.environ.get('COMPANY_ID'),
            cert_file=os.environ.get('CERT_FILE'),
            cert_key=os.environ.get('KEY_FILE')
        )
    
    @vcr.use_cassette('tests/fixtures/vcr_cassetes/login_ok.yaml')
    def test__BeedataApiClient_ok(self):
        # given the correct credentials from a beedata client
        credentials = self.beedata_api_correct_credentials

        # when we create a new instances of BeedataApiClient
        beedata_api = asyncio.run(BeedataApiClient.create(**credentials))

        # then we have an instance of BeedataApiClient
        self.assertIsInstance(beedata_api, BeedataApiClient)
        # and a new api_session is created
        self.assertIsNotNone(beedata_api.api_session)

    @vcr.use_cassette('tests/fixtures/vcr_cassetes/login_ko.yaml')
    def test__BeedataApiClient_ko(self):
        # given the correct credentials from a beedata client
        credentials = self.beedata_api_bad_credentials

        # when we create a new instances of BeedataApiClient
        with self.assertRaises(ApiException) as exception_manager:
            beedata_api = asyncio.run(BeedataApiClient.create(**credentials))

        # then we have an ApiException instance with an unauthorized message
        error = exception_manager.exception
        self.assertEqual(str(error), 'Authentication failure')