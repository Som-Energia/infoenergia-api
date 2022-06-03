import asyncio
from unittest import mock

import aiohttp
import fakeredis
import pytest
from aiohttp.test_utils import unittest_run_loop
from motor.motor_asyncio import AsyncIOMotorClient
from pony.orm import db_session

from infoenergia_api.contrib import Beedata, BeedataApiClient
from tests.base import BaseTestCaseAsync


class TestReport:

    async def test__post_contracts(self, app, auth_token, mock_process_reports):
        mock_process_reports.return_value = []
        _, response = await app.asgi_client.post(
            '/reports/',
            headers={
                'Authorization': 'Bearer {}'.format(auth_token)
            },
            json={
              'id': "summer_2020",
              'contract_ids': ["0180471", "0010012", "1000010"],
              'type': 'CCH',
              'create_at': "2020-01-01",
              'month': '202011'
            },
        )

        assert response.status == 200
        assert response.json == {'reports': 3}

    async def test__post_photovoltaic_contracts(self, app, auth_token, mock_process_reports):
        mock_process_reports.return_value = []
        
        _, response = await app.asgi_client.post(
            '/reports/',
            headers={
                'Authorization': 'Bearer {}'.format(auth_token)
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

        assert response.status == 200
        assert response.json == {'reports': 3}

    async def test__login_to_beedata(self, bapi, app):
        bapi = Beedata(bapi, app.ctx.mongo_client, app.ctx.redis)
        status = await bapi.api_client.login(
            app.config.USERNAME, app.config.PASSWORD
        )

        assert status.token != None


class TestBeedataReports:

    async def test__download_one_report(self, bapi):
        status, report = await bapi.download_report(
            contract_id="0090438",
            month='202011',
            report_type='CCH'
        )
        assert status == 200
        assert report is not None

    async def test__download_one_report__wrongid(self, bapi):
        status, report = await bapi.download_report(
            contract_id="1090438",
            month='202011',
            report_type='CCH'
        )
        assert status == 200
        assert report is None

    async def test__process_one_valid_report(self, beedata):
        beedata.save_report = mock.AsyncMock(return_value='1234')
        
        result = await beedata.process_one_report(
            contract_id='0090438',
            month='202011',
            report_type='CCH',
        )
        assert result is True

    async def test__process_one_invalid_report(self, beedata):
        beedata.save_report = mock.AsyncMock(return_value='')

        result = await beedata.process_one_report(
            contract_id='090438',
            month='202011',
            report_type='CCH',
        )
        assert result is False

    async def test__insert_or_update_report(self, app, beedata):
        report_type = 'infoenergia_reports'
        report = [{
            'contractId': '1234567',
            '_updated': "2020-08-18T12:06:23Z",
            '_created':  "2020-08-18T12:06:23Z",
            'month': '202009',
            'type': 'CCH',
            'results': {},
        }]
        report_id = await beedata.save_report(report, report_type)
        expected_report = await app.ctx.mongo_client.somenergia.infoenergia_reports.find_one(report_id[0])
        assert report_id[0] == expected_report['_id']

    async def test__download_one_report__expected_infoenergia_fields(self, bapi):
        status, report = await bapi.download_report(
            contract_id="0068759",
            month='202011',
            report_type='infoenergia_reports'
        )
        assert status == 200
        assert report is not None
        assert 'seasonalProfile' in report[0]['results']

    async def test__download_one_report__expected_photovoltaic_fields(self, bapi):
        status, report = await bapi.download_report(
            contract_id="0068759",
            month=None,
            report_type='photovoltaic_reports'
        )
        assert status == 200
        assert report is not None
        assert 'pvAutoSize' in report[0]['results']
