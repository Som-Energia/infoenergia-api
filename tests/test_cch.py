from infoenergia_api.contrib import (
    TgCchF5d,
    TgCchF1,
    TgCchP1,
    TgCchGennetabeta,
    TgCchAutocons,
)
import pytest
import datetime

class TestCchRequest:
    async def test__get_f5d_by_id__2A(
        self, app, auth_token, scenarios, mocked_next_cursor
    ):
        params = {
            "from_": "2018-11-16",
            "to_": "2018-12-16",
            "limit": 10,
            "type": "tg_cchfact",
        }
        _, response = await app.asgi_client.get(
            "/cch/{}".format(scenarios["f5d"]["contractId"]),
            headers={"Authorization": "Bearer {}".format(auth_token)},
            params=params,
        )
        assert response.status == 200
        assert response.json["count"] == 10
        assert response.json["total_results"] == 721
        assert (
            response.json["cursor"]
            == "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0="
        )
        assert response.json[
            "next_page"
        ] == "http://{}/cch/0067411?type=tg_cchfact&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=10".format(
            response.url.netloc.decode()
        )
        assert len(response.json["data"]) == 10

    async def test__get_f5d__all_contracts(
        self, app, auth_token, scenarios, mocked_next_cursor
    ):

        params = {"to_": "2019-10-08", "type": "tg_cchfact"}
        _, response = await app.asgi_client.get(
            "/cch",
            params=params,
            headers={"Authorization": "Bearer {}".format(auth_token)},
            timeout=None,
        )
        assert response.status == 200
        assert response.json["count"] == 50
        assert response.json["total_results"] == 16583
        assert (
            response.json["cursor"]
            == "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0="
        )
        assert response.json[
            "next_page"
        ] == "http://{}/cch?type=tg_cchfact&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=50".format(
            response.url.netloc.decode()
        )
        assert len(response.json["data"]) == 50

    async def test__get_f5d_without_permission(self, app, auth_token, scenarios):
        params = {"from_": "2018-11-16", "to_": "2018-12-16", "type": "tg_cchfact"}
        _, response = await app.asgi_client.get(
            "/cch/{}".format(scenarios["f5d"]["contractId"]),
            params=params,
            headers={"Authorization": "Bearer {}".format(auth_token)},
            timeout=None,
        )

        assert response.status == 200
        assert response.json == {"count": 0, "total_results": 0, "data": []}

    async def test__get_p5d__for_contract_id(self, app, auth_token, scenarios):
        params = {"from_": "2017-12-29", "to_": "2018-01-01", "type": "tg_cchval"}
        _, response = await app.asgi_client.get(
            "/cch/{}".format(scenarios["p5d"]["contractId"]),
            params=params,
            headers={"Authorization": "Bearer {}".format(auth_token)},
        )
        assert response.status == 200
        assert response.json == {
            "count": 24,
            "total_results": 24,
            "data": scenarios["p5d"]["cch_data"],
        }

    async def test__get_p5d_without_permission(self, app, auth_token, scenarios):
        params = {"type": "tg_cchval"}
        _, response = await app.asgi_client.get(
            "/cch/{}".format(scenarios["p5d"]["contractId"]),
            params=params,
            headers={"Authorization": "Bearer {}".format(auth_token)},
        )

        assert response.status == 200
        assert response.json == {"count": 0, "total_results": 0, "data": []}

    async def test__get_f1_by_id(self, app, auth_token, scenarios, mocked_next_cursor):
        params = {
            "from_": "2018-11-16",
            "to_": "2023-01-20",
            "limit": 10,
            "type": "tg_f1",
        }
        _, response = await app.asgi_client.get(
            "/cch/{}".format(scenarios["tg_f1"]["contractId"]),
            headers={"Authorization": "Bearer {}".format(auth_token)},
            params=params,
        )
        assert response.status == 200
        assert response.json["count"] == 10
        assert response.json["total_results"] == 13201
        assert (
            response.json["cursor"]
            == "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0="
        )
        assert response.json[
            "next_page"
        ] == "http://{}/cch/{}?type=tg_f1&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=10".format(
            response.url.netloc.decode(), scenarios["tg_f1"]["contractId"]
        )
        assert len(response.json["data"]) == 10

    async def test__get_p1__for_contract_id(
        self, app, auth_token, scenarios, mocked_next_cursor
    ):

        params = {"from_": "2017-12-21", "to_": "2018-01-01", "type": "P1", "limit": 1}
        _, response = await app.asgi_client.get(
            "/cch/{}".format(scenarios["p1"]["contractId"]),
            params=params,
            headers={"Authorization": "Bearer {}".format(auth_token)},
        )

        assert response.status == 200
        assert response.json == {
            "count": 1,
            "total_results": 265,
            "data": scenarios["p1"]["cch_data"],
            "cursor": mocked_next_cursor,
            "next_page": "http://{}/cch/0020309?type=P1&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                response.url.netloc.decode()
            ),
        }

    async def test__get_p2__for_all_contracts(
        self, app, auth_token, scenarios, mocked_next_cursor
    ):

        params = {"from_": "2020-01-28", "to_": "2020-01-29", "type": "P2", "limit": 1}
        _, response = await app.asgi_client.get(
            "/cch/",
            params=params,
            headers={"Authorization": "Bearer {}".format(auth_token)},
        )

        assert response.status == 200
        assert response.json == {
            "count": 1,
            "total_results": 629,
            "data": scenarios["p2"]["cch_data"],
            "cursor": mocked_next_cursor,
            "next_page": "http://{}/cch?type=P2&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=1".format(
                response.url.netloc.decode()
            ),
        }


class TestCchModels:

    # Build queries for ERP curves

    async def assert_build_erp_query(self, filters: dict, expected_query: list[tuple]):
        query = await TgCchF1.build_query(filters)
        assert query == expected_query

    async def test__build_query__erp_model__no_filters(self):
        await self.assert_build_erp_query(dict(), [])

    @pytest.mark.parametrize('parameter,value,expected', [
        ('cups', 'a_cups',
            [('name', '=', 'a_cups'),]),
        ('from_', '2022-01-01',
            [('datetime', '>=', '2022-01-01'),]),
        ('to_', '2022-01-01',
            [('datetime', '<=', '2022-01-01'),]),
        ('downloaded_from', '2022-01-01',
            [('create_at', '>=', '2022-01-01'),]),
        ('downloaded_to', '2022-01-01',
            [('create_at', '<=', '2022-01-01'),]),
    ])
    async def test__build_query__erp_model__with_single_parameter(self, parameter, value, expected):
        await self.assert_build_erp_query({ parameter: [value]}, expected)

    async def test__build_query__erp_model__with_several_parameters(self):
        cups = "a_cups"
        await self.assert_build_erp_query(dict(
            cups = [cups],
            **{'from_': ['2022-01-01']}
        ),[
            ('datetime', '>=', '2022-01-01'),
            ('name', '=', cups),
        ])

    # Build queries for Mongo curves

    async def assert_build_mongo_query(self, filters, expected_query):
        from infoenergia_api.utils import get_cch_query
        filters = dict(filters)
        filters.setdefault('type', "tg_f1")
        cups = filters.pop('cups',None)
        query = await get_cch_query(filters, cups)
        assert query == expected_query

    async def test__build_query__mongo_model__no_filters(self):
        await self.assert_build_mongo_query(dict(), {})

    @pytest.mark.parametrize('parameter,value,expected', [
        ('cups', 'a_cups',
            {'name': {'$regex': '^a_cups'}}),
        ('from_', '2022-01-01',
            {'datetime': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('to_', '2022-01-01',
            {'datetime': {'$lte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('downloaded_from', '2022-01-01',
            {'create_at': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('downloaded_to', '2022-01-01',
            {'create_at': {'$lte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('type', 'p1',
            {'type': {'$eq': 'p'}}),
        ('type', 'p2',
            {'type': {'$eq': 'p4'}}),
    ])
    async def test__build_query__mongo_model__with_single_parameter(self, parameter, value, expected):
        await self.assert_build_mongo_query({ parameter: [value]}, expected)

    async def test__build_query__mongo_model__with_several_parameters(self):
        cups = "a_cups"
        await self.assert_build_mongo_query(dict(
            cups = [cups],
            **{'from_': ['2022-01-01']}
        ),{
            'datetime': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)},
            'name': {'$regex': '^a_cups'},
        })

    # Instanciating curve points

    async def test__create_f5d(self, f5d_id, app):
        f5d = await TgCchF5d.create(f5d_id)
        assert isinstance(f5d, TgCchF5d)

    async def test__get_f5d_measurements(self, f5d_id, app):
        f5d = await TgCchF5d.create(f5d_id)
        measurements = f5d.measurements
        assert measurements == {
            "ai": 496,
            "ao": 0,
            "date": "2018-11-15 23:00:00+0000",
            "dateDownload": "2019-01-03 10:36:03",
            "dateUpdate": "2019-01-03 16:56:28",
            "r1": 134,
            "r2": 0,
            "r3": 0,
            "r4": 0,
            "season": 0,
            "source": 1,
            "validated": True,
        }

    async def test__create_f1(self, f1_id, event_loop):
        f1 = await TgCchF1.create(f1_id)
        assert isinstance(f1, TgCchF1)

    async def test__get_f1_measurements(self, f1_id, event_loop):
        f1 = await TgCchF1.create(f1_id)
        measurements = f1.measurements
        assert measurements == {
            "season": 1,
            "ai": 5.0,
            "ao": 0.0,
            "r1": 3.0,
            "r2": 0.0,
            "r3": 0.0,
            "r4": 0.0,
            "source": 1,
            "validated": 0,
            "date": "2022-05-31 22:00:00+0000",
            "dateDownload": "2022-09-19 13:44:56",
            "dateUpdate": "2022-09-19 13:44:56",
            "reserve1": 0.0,
            "reserve2": 0.0,
            "measureType": 11,
        }

    async def test__get_P1_measurements(self, p1_id, app):
        p1 = await TgCchP1.create(p1_id)
        measurements = p1.measurements
        assert measurements == {
            "ai": 0.0,
            "aiquality": 0,
            "ao": 0.0,
            "aoQuality": 0,
            "date": "2017-12-20 22:00:00+0000",
            "dateDownload": "2020-01-14 10:45:53",
            "dateUpdate": "2020-01-14 10:45:53",
            "measureType": 11,
            "r1": 0.0,
            "r1Quality": 0,
            "r2": 0.0,
            "r2Quality": 0,
            "r3": 0.0,
            "r3Quality": 0,
            "r4": 0.0,
            "r4Quality": 0,
            "reserve1": 0,
            "reserve1Quality": 128,
            "reserve2": 0,
            "reserve2Quality": 128,
            "season": 0,
            "source": None,
            "type": "p",
            "validated": False,
        }

    async def test__get_P2_measurements(self, p2_id, app):
        p2 = await TgCchP1.create(p2_id)
        measurements = p2.measurements
        assert measurements == {
            "ai": 0.0,
            "aiquality": 0,
            "ao": 0.0,
            "aoQuality": 0,
            "date": "2020-01-16 22:00:00+0000",
            "dateDownload": "2020-01-28 11:50:33",
            "dateUpdate": "2020-01-28 11:50:33",
            "measureType": 11,
            "r1": 0.0,
            "r1Quality": 0,
            "r2": 0.0,
            "r2Quality": 0,
            "r3": 0.0,
            "r3Quality": 0,
            "r4": 0.0,
            "r4Quality": 0,
            "reserve1": 0.0,
            "reserve1Quality": 128,
            "reserve2": 0.0,
            "reserve2Quality": 128,
            "season": 0,
            "source": 1,
            "type": "p4",
            "validated": False,
        }

    async def test__create_gennetabeta(self, gennetabeta_id, event_loop):
        point = await TgCchGennetabeta.create(gennetabeta_id)
        assert isinstance(point, TgCchGennetabeta)

    async def test__get_gennetabeta_measurements(self, gennetabeta_id, event_loop):
        point = await TgCchGennetabeta.create(gennetabeta_id)
        measurements = point.measurements
        assert measurements == {
            "ae": 0,
            "ai": 0,
            "bill": "F4001N07516369",
            "date": "2020-07-13 01:00:00+0200",
            "dateDownload": "2021-06-26 04:54:42",
            "dateUpdate": "2021-06-26 04:55:03",
            "r1": False,
            "r2": False,
            "r3": False,
            "r4": False,
            "season": 1,
            "source": False,
            "validated": ""
        }

    async def test__create_autocons(self, autocons_id, event_loop):
        point = await TgCchAutocons.create(autocons_id)
        assert isinstance(point, TgCchAutocons)

    async def test__get_autocons_measurements(self, autocons_id, event_loop):
        point = await TgCchAutocons.create(autocons_id)
        measurements = point.measurements
        assert measurements == {
            "ae": False,
            "ai": 0,
            "bill": "103N210600880779",
            "date": "2021-05-01 01:00:00+0200",
            "dateDownload": "2021-06-16 08:09:56",
            "dateUpdate": "2021-06-26 07:23:11",
            "r1": False,
            "r2": False,
            "r3": False,
            "r4": False,
            "season": 1,
            "source": False,
            "validated": ""
            }


