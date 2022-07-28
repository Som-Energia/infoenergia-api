from infoenergia_api.contrib import TgCchF5d, TgCchF1, TgCchP1


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
        assert response.json == {
            "count": 10,
            "total_results": 721,
            "cursor": mocked_next_cursor,
            "next_page": "http://{}/cch/0067411?type=tg_cchfact&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=10".format(
                response.url.netloc.decode()
            ),
            "data": scenarios["f5d"]["cch_data"],
        }

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
        assert response.json == {
            "count": 50,
            "total_results": 409913,
            "cursor": mocked_next_cursor,
            "next_page": "http://{}/cch?type=tg_cchfact&cursor=N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0=&limit=50".format(
                response.url.netloc.decode
            ),
            "data": scenarios["f5d_all"]["cch_data"],
        }

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
                response.url.netloc.decode
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
                response.url.netloc.decode
            ),
        }


class TestCchModels:
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

    async def test__create_f1(self, f1_id, app):
        f1 = await TgCchF1.create(f1_id)
        assert isinstance(f1, TgCchF1)

    async def test__get_f1_measurements(self, f1_id, app):
        f1 = await TgCchF1.create(f1_id)
        measurements = f1.measurements
        assert measurements == {
            "ai": 14.0,
            "ao": 0.0,
            "date": "2017-12-01 22:00:00+0000",
            "dateUpdate": "2020-01-14 10:44:54",
            "season": 0,
            "validated": False,
            "r1": 1.0,
            "r2": 0.0,
            "r3": 0.0,
            "r4": 2.0,
            "reserve1": 0,
            "reserve2": 0,
            "source": 1,
            "measureType": 11,
            "dateDownload": "2020-01-14 10:44:54",
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
