import os

import pytest
import vcr
from config import config

from infoenergia_api.contrib.beedata_api import BeedataApiClient
from infoenergia_api.contrib.beedata_api.exceptions import ApiError


class TestBeedataApiClient:

    REPORT_KEYS = [
        "seasonalProfile",
        "last3MonthsProfile",
        "weeklyAvgConsumeLast3Months",
        "dailyTypicalProfileSummer",
        "dailyTypicalProfileWinter",
        "dailyTypicalProfileLast12Months",
        "dailyTypicalProfileLast3Months",
        "weeklyAvgConsumeWinter",
        "distributionByPeriods",
        "weeklyAvgConsumeLast12Months",
        "distributionByTypeOfUse",
        "weeklyAvgConsumeSummer",
    ]

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassetes/login_ok.yaml", record_mode=config.RECORD_MODE
    )
    async def test__BeedataApiClient__ok(
        self,
        # given the correct credentials from a beedata client
        beedata_api_correct_credentials,
    ):

        # when we create a new instances of BeedataApiClient
        beedata_api = await BeedataApiClient.create(**beedata_api_correct_credentials)

        # then we have an instance of BeedataApiClient
        assert isinstance(beedata_api, BeedataApiClient)
        # and a new api_session is created
        assert beedata_api.api_session is not None

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassetes/login_ko.yaml", record_mode=config.RECORD_MODE
    )
    async def test__BeedataApiClient__ko(
        self,
        # given the correct credentials from a beedata client
        beedata_api_bad_credentials,
    ):

        # when we create a new instances of BeedataApiClient
        with pytest.raises(ApiError) as exception_manager:
            beedata_api = await BeedataApiClient.create(**beedata_api_bad_credentials)

        # then we have an ApiException instance with an unauthorized message
        error = exception_manager.value
        assert str(error) == "Authentication failure"

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassetes/report.yaml", record_mode=config.RECORD_MODE
    )
    async def test__download_one_report(self, bapi):
        status, report = await bapi.download_report(
            contract_id="0121850", month="202209", report_type="infoenergia_reports"
        )
        assert status == 200
        assert report is not None
        assert sorted(self.REPORT_KEYS) == sorted(report["results"].keys())

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassetes/report__wrongid.yaml",
        record_mode=config.RECORD_MODE,
    )
    async def test__download_one_report__wrongid(self, bapi):
        status, report = await bapi.download_report(
            contract_id="1090438", month="202011", report_type="infoenergia_reports"
        )
        assert status == 200
        assert report is None
