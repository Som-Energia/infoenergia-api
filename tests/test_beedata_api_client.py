import os

import pytest
import vcr

from infoenergia_api.contrib import ApiException, BeedataApiClient


class TestBeedataApiClient():

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
    async def test__BeedataApiClient__ok(self):
        # given the correct credentials from a beedata client
        credentials = self.beedata_api_correct_credentials

        # when we create a new instances of BeedataApiClient
        beedata_api = await BeedataApiClient.create(**credentials)

        # then we have an instance of BeedataApiClient
        assert isinstance(beedata_api, BeedataApiClient)
        # and a new api_session is created
        assert beedata_api.api_session is not None

    @vcr.use_cassette('tests/fixtures/vcr_cassetes/login_ko.yaml')
    async def test__BeedataApiClient__ko(self):
        # given the correct credentials from a beedata client
        credentials = self.beedata_api_bad_credentials

        # when we create a new instances of BeedataApiClient
        with pytest.raises(ApiException) as exception_manager:
            beedata_api = await BeedataApiClient.create(**credentials)

        # then we have an ApiException instance with an unauthorized message
        error = exception_manager.value
        assert str(error) == 'Authentication failure'