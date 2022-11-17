from unittest import mock
import pytest

from pony.orm import db_session

from infoenergia_api.api.reports import create_report_request, ReportRequest
from infoenergia_api.contrib.reports import BeedataReports


class TestReportRequestModel:
    async def test__create_report_request(
        self,
        db,
        # given an UUID id,
        uuid_id,
        # and a raw report request
        raw_report_request,
    ):
        # when we create a new report request
        report_request = await create_report_request(uuid_id, raw_report_request)

        # then we have an instance of a ReportRequest model
        assert isinstance(report_request, ReportRequest)
        # and is saved in database
        with db_session:
            assert ReportRequest.get(id=uuid_id) is not None


class TestBeedataReports:
    def test__beedata_report_instance(
        self,
        # given an instance of beedata api client
        bapi,
        # a mongo connection
        mongo_conn,
        # and a report request
        report_request__one_contract,
    ):
        # when we create a instance of a beedata report
        beedata_reports = BeedataReports(bapi, mongo_conn, report_request__one_contract)

        # then we have a valid instance of beedata reports class
        assert isinstance(beedata_reports, BeedataReports)

    async def test__process_reports__one_report(
        self,
        # given a valid instance of beedata report
        beedata_reports__one_report,
    ):
        # when we process all reports in the request
        result = await beedata_reports__one_report.process_reports()
        assert result == ([], beedata_reports__one_report.reports)

    async def test__process_reports__multiple_reports(
        self,
        # given a valid instance of beedata report
        beedata_reports__multiple_reports,
    ):
        # when we process all reports in the request
        _, result = await beedata_reports__multiple_reports.process_reports()
        assert sorted(result) == sorted(beedata_reports__multiple_reports.reports)

    async def test__process_multiple_invalid_report(
        self,
        # given a incorrect instance of a beedata report
        beedata_reports__invalid_multiple_reports,
    ):
        # when we process all reports in the request
        (
            unprocess_reports,
            process_reports,
        ) = await beedata_reports__invalid_multiple_reports.process_reports()

        assert len(unprocess_reports) == 1
        assert len(process_reports) == 2

    @pytest.mark.skip("to redifine test")
    async def test__insert_or_update_report(self, app, beedata):
        report_type = "infoenergia_reports"
        report = [
            {
                "contractId": "1234567",
                "_updated": "2020-08-18T12:06:23Z",
                "_created": "2020-08-18T12:06:23Z",
                "month": "202009",
                "type": "CCH",
                "results": {},
            }
        ]
        report_id = await beedata.save_report(report, report_type)
        expected_report = (
            await app.ctx.mongo_client.somenergia.infoenergia_reports.find_one(
                report_id[0]
            )
        )
        assert report_id[0] == expected_report["_id"]

    @pytest.mark.skip("to redifine test")
    async def test__download_one_report__expected_infoenergia_fields(self, bapi):
        status, report = await bapi.download_report(
            contract_id="0068759", month="202011", report_type="infoenergia_reports"
        )
        assert status == 200
        assert report is not None
        assert "seasonalProfile" in report[0]["results"]

    @pytest.mark.skip("to redifine test")
    async def test__download_one_report__expected_photovoltaic_fields(self, bapi):
        status, report = await bapi.download_report(
            contract_id="0068759", month=None, report_type="photovoltaic_reports"
        )
        assert status == 200
        assert report is not None
        assert "pvAutoSize" in report[0]["results"]


class TestReport:
    async def test__post_contracts(self, app, auth_token, mock_process_reports):
        mock_process_reports.return_value = []
        _, response = await app.asgi_client.post(
            "/reports/",
            headers={"Authorization": "Bearer {}".format(auth_token)},
            json={
                "id": "summer_2020",
                "contract_ids": ["0180471", "0010012", "1000010"],
                "type": "CCH",
                "create_at": "2020-01-01",
                "month": "202011",
            },
        )

        assert response.status == 200
        assert response.json == {"reports": 3}

    async def test__post_photovoltaic_contracts(
        self, app, auth_token, mock_process_reports
    ):
        mock_process_reports.return_value = []

        _, response = await app.asgi_client.post(
            "/reports/",
            headers={"Authorization": "Bearer {}".format(auth_token)},
            json={
                "id": "summer_2020",
                "contract_ids": ["0068759", "0010012", "1000010"],
                "type": "photovoltaic_reports",
                "create_at": "2020-01-01",
                "month": "202011",
            },
            timeout=None,
        )

        assert response.status == 200
        assert response.json == {"reports": 3}
