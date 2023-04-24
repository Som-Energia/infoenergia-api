from infoenergia_api.contrib import (
    TgCchF5d,
    TgCchF1,
    TgCchP1,
    TgCchGennetabeta,
    TgCchAutocons,
    cch_model,
)
from infoenergia_api.contrib.cch import (
    get_curve,
    MongoCurveRepository,
    TimescaleCurveRepository,
)

import pytest
import datetime
from yamlns.pytestutils import ns, assert_ns_equal, assert_ns_contains

from infoenergia_api.contrib.erp import get_erp_instance

def assert_response_equal(response, expected, expected_status=200):
    if type(expected) == str:
        expected = ns.loads(expected)
    assert_ns_equal(
        ns(
            status = response.status,
            json = response.json,
        ), ns(
            status = expected_status,
            json = expected,
        ))

def assert_response_contains(response, expected, expected_status=200):
    if type(expected) == str:
        expected = ns.loads(expected)
    assert_ns_contains(
        ns(
            status = response.status,
            json = response.json,
        ), ns(
            status = expected_status,
            json = expected,
        ))

@pytest.fixture
def cchquery(app, auth_token, mocked_next_cursor):
    async def inner(contract_id=None, params={}):
        url="/cch/{}".format(contract_id) if contract_id else "/cch"
        _, response = await app.asgi_client.get(
            url,
            headers={"Authorization": "Bearer {}".format(auth_token)},
            params=params,
        )
        return response
    return inner

@pytest.fixture
def unprivileged_cchquery(app, unprivileged_auth_token, mocked_next_cursor):
    async def inner(contract_id=None, params={}):
        url="/cch/{}".format(contract_id) if contract_id else "/cch"
        _, response = await app.asgi_client.get(
            url,
            headers={"Authorization": "Bearer {}".format(unprivileged_auth_token)},
            params=params,
        )
        return response
    return inner


class TestCchRequest:
    async def test__get_f5d_by_id__2A(self, cchquery, scenarios):
        response = await cchquery(
            contract_id=scenarios["f5d"]["contractId"],
            params={
                "from_": "2018-11-16",
                "to_": "2018-12-16",
                "limit": 10,
                "type": "tg_cchfact",
            },
        )
        cursor = response.json.get("cursor", "NO_CURSOR_RETURNED")
        assert_response_contains(response, ns(
            count=10,
            total_results=745,
            cursor=cursor,
            next_page="http://{}/cch/0067411?type=tg_cchfact&cursor={}&limit=10".format(
                response.url.netloc.decode(),
                cursor,
            ),
        ))
        assert len(response.json["data"]) == 10

    async def test__get_f5d__all_contracts(self, cchquery, scenarios):
        response = await cchquery(
            params = {
                "to_": "2019-10-08",
                "type": "tg_cchfact",
            },
            #timeout=None, # TODO: review this
        )
        cursor = response.json.get("cursor", "NO_CURSOR_RETURNED")
        assert_response_contains(response, ns(
            count=50,
            total_results=16583,
            cursor=cursor,
            next_page="http://{}/cch?type=tg_cchfact&cursor={}&limit=50".format(
                response.url.netloc.decode(),
                cursor,
            ),
        ))
        assert len(response.json["data"]) == 50

    async def test__get_f5d_without_permission(self, unprivileged_cchquery, scenarios):
        response = await unprivileged_cchquery(
            contract_id=scenarios["f5d"]["contractId"],
            params = {
                "type": "tg_cchfact",
                "from_": "2018-11-16",
                "to_": "2018-12-16",
            },
        )
        assert_response_equal(response, ns(
            count=0,
            total_results=0,
            data=[],
        ))

    async def test__get_p5d__for_contract_id(self, cchquery, scenarios):
        response = await cchquery(
            contract_id=scenarios["p5d"]["contractId"],
            params = {
                "type": "tg_cchval",
                "from_": "2017-12-29",
                "to_": "2018-01-01",
            }
        )
        assert_response_equal(response, ns(
            count=24,
            total_results=24,
            data=scenarios["p5d"]["cch_data"],
        ))

    async def test__get_p5d_without_permission(self, unprivileged_cchquery, scenarios):
        response = await unprivileged_cchquery(
            contract_id=scenarios["p5d"]["contractId"],
            params = {
                "type": "tg_cchval",
            },
        )
        assert_response_equal(response, ns(
            count=0,
            total_results=0,
            data=[],
        ))

    async def test__get_f1_by_id(self, cchquery, scenarios):
        response = await cchquery(
            contract_id=scenarios["tg_f1"]["contractId"],
            params = {
                "from_": "2018-11-16",
                "to_": "2023-01-20",
                "limit": 10,
                "type": "tg_f1",
            }
        )
        cursor = response.json.get("cursor", "NO_CURSOR_RETURNED")
        assert_response_contains(response, ns(
            count=10,
            total_results=13201,
            cursor=cursor,
            next_page="http://{}/cch/{}?type=tg_f1&cursor={}&limit=10".format(
                response.url.netloc.decode(),
                scenarios["tg_f1"]["contractId"],
                cursor,
            ),
        ))
        assert len(response.json["data"]) == 10

    async def test__get_p1__for_contract_id(self, cchquery, scenarios):
        response = await cchquery(
            contract_id=scenarios["p1"]["contractId"],
            params = {
                "type": "P1",
                "from_": "2017-12-21",
                "to_": "2018-01-01",
                "limit": 1,
            }
        )
        cursor = response.json.get("cursor", "NO_CURSOR_RETURNED")
        assert_response_equal(response, ns(
            count=1,
            total_results=289,
            data=scenarios["p1"]["cch_data"],
            cursor=cursor,
            next_page="http://{}/cch/0020309?type=P1&cursor={}&limit=1".format(
                response.url.netloc.decode(),
                cursor,
            ),
        ))

    async def test__get_p2__for_all_contracts(self, cchquery, scenarios, yaml_snapshot):
        response = await cchquery(
            params = {
                "type": "P2",
                "from_": "2020-01-28",
                "to_": "2020-01-28",
                "limit": 1,
            }
        )
        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))

    contract_collective_self_consumption = '0069752'
    contract_with_readings = contract_collective_self_consumption # also complies
    # Most Px curves are received with CUPS with a different suffix
    # (border point suffix) than the contract as in ERP: 0F vs xP
    #TODO: Make nP suffix to work
    contract_with_px_and_0F_cups = '0188943'
    contract_with_f1_curves = '0220579'

    @pytest.mark.parametrize('curve_type,contract_id', [
        ('tg_f1', contract_with_f1_curves),
        ('tg_cchval', contract_with_readings),
        ('tg_cchfact', contract_with_readings),
        ('tg_gennetabeta', contract_collective_self_consumption),
        ('tg_cchautocons', contract_collective_self_consumption),
        ('P1', contract_with_px_and_0F_cups),
        ('P2', contract_with_px_and_0F_cups), # 4 times more curves than P1 but paginated
    ])
    async def test__two_days_curve(self, curve_type, contract_id, cchquery, yaml_snapshot):
        response = await cchquery(
            contract_id=contract_id,
            params = {
                "type": curve_type,
                "from_": "2022-11-29",
                "to_": "2022-11-30",
            }
        )
        if response.json.get('data',[]):
            response.json['data'] = list(sorted(
                response.json['data'], key=lambda x: x.get('measurements',{}).get('date','')
            ))
        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))

    def get_cups(self, contract_number=None):
        erp = get_erp_instance()
        contract_obj = erp.model("giscedata.polissa")
        contract_id = contract_obj.search([
            ("name", "=", contract_number),
        ])[0]
        return contract_obj.read(contract_id, ["cups"])["cups"][1]

    @pytest.mark.parametrize('curve_type,contract_number', [
        #('tg_f1', contract_with_f1_curves),
        #('tg_cchval', contract_with_readings),
        ('tg_cchfact', contract_with_readings),
        #('tg_gennetabeta', contract_collective_self_consumption),
        #('tg_cchautocons', contract_collective_self_consumption),
        #('P1', contract_with_px_and_0F_cups),
        #('P2', contract_with_px_and_0F_cups), # 4 times more curves than P1 but paginated
    ])
    async def test__get_curve__two_days(self, curve_type, contract_number, cchquery, yaml_snapshot):
        cups = self.get_cups(contract_number)
        curve = await get_curve(
            type=curve_type,
            cups=cups,
            start="2022-11-29",
            end="2022-11-30",
        )
        yaml_snapshot(ns(
            curve=curve,
        ))


class TestMongoCurveRepository:
    async def assert_build_mongo_query(self, filters, expected_query):
        query = MongoCurveRepository().build_query(**filters)
        assert query == expected_query

    async def test__build_query__no_filters(self):
        await self.assert_build_mongo_query(dict(), {})

    @pytest.mark.parametrize('parameter,value,expected', [
        ('cups', '12345678901234567890_this_should_disappear',
            {'name': {'$regex': '^12345678901234567890'}}),
        ('start', '2022-01-01',
            {'datetime': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('end', '2022-01-01',
            {'datetime': {'$lte': datetime.datetime(2022, 1, 2, 0, 0)}}),
        ('downloaded_from', '2022-01-01',
            {'create_at': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('downloaded_to', '2022-01-01',
            {'create_at': {'$lte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('type', 'p', # P1
            {'type': {'$eq': 'p'}}),
        ('type', 'p4', # P2
            {'type': {'$eq': 'p4'}}),
    ])
    async def test__build_query__with_single_parameter(self, parameter, value, expected):
        await self.assert_build_mongo_query({ parameter: value}, expected)

    async def test__build_query__with_several_parameters(self):
        cups = "a_cups"
        await self.assert_build_mongo_query(dict(
            cups = cups,
            start = '2022-01-01',
        ),{
            'datetime': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)},
            'name': {'$regex': '^a_cups'},
        })

    async def test__build_query__with_from_and_to(self):
        await self.assert_build_mongo_query({
            'start': '2022-01-01',
            'end': '2022-01-02',
        },{
            'datetime': {
                # Both conditions on datetime are joined
                '$gte': datetime.datetime(2022, 1, 1, 0, 0),
                '$lte': datetime.datetime(2022, 1, 3, 0, 0),
            },
        })

    async def test__build_query__with_downloaded_from_and_to(self):
        await self.assert_build_mongo_query({
            'downloaded_from': '2022-01-01',
            'downloaded_to': '2022-01-02',
        },{
            'create_at': {
                # Both conditions on datetime are joined
                '$gte': datetime.datetime(2022, 1, 1, 0, 0),
                '$lte': datetime.datetime(2022, 1, 2, 0, 0),
            },
        })


class TestTimescaleCurveRepository:
    async def assert_build_query(self, filters, expected_query):
        query = await TimescaleCurveRepository().build_query(**filters)
        assert query == expected_query

    async def test__build_query__no_filters(self):
        await self.assert_build_query(dict(), [])

    @pytest.mark.parametrize('parameter,value,expected', [
        ('cups', '12345678901234567890_this_should_disappear',
            ["name ILIKE '12345678901234567890%'"]),
    ])
    async def test__build_query__with_single_parameter(self, parameter, value, expected):
        await self.assert_build_query({ parameter: value}, expected)




class TestCchModels:

    # Build queries for ERP curves

    async def assert_build_erp_query(self, filters, expected_query, model=TgCchGennetabeta):
        query = await model.build_query(filters)
        assert query == expected_query

    async def test__build_query__erp_mongo_model__no_filters(self):
        await self.assert_build_erp_query(dict(), [])

    @pytest.mark.parametrize('parameter,value,expected', [
        ('cups', '12345678901234567890_this_should_be_kept',
            [('name', '=', '12345678901234567890_this_should_be_kept'),]),
        ('from_', '2022-01-01',
            [('datetime', '>=', '2022-01-01'),]),
        ('to_', '2022-01-01',
            [('datetime', '<', '2022-01-02'),]), # the date is next day
        ('downloaded_from', '2022-01-01',
            [('create_at', '>=', '2022-01-01'),]),
        ('downloaded_to', '2022-01-01',
            [('create_at', '<=', '2022-01-01'),]),
    ])
    async def test__build_query__erp_mongo_model__with_single_parameter(self, parameter, value, expected):
        await self.assert_build_erp_query({ parameter: value}, expected)

    async def test__build_query__erp_mongo_model__with_several_parameters(self):
        cups = "a_cups"
        await self.assert_build_erp_query(dict(
            cups = cups,
            **{'from_': '2022-01-01'}
        ),[
            ('datetime', '>=', '2022-01-01'),
            ('name', '=', cups),
        ])

    @pytest.mark.parametrize('parameter,value,expected', [
        ('cups', '12345678901234567890_this_should_be_kept',
            [('name', '=', '12345678901234567890_this_should_be_kept'),]),
        ('from_', '2022-01-01',
            [('utc_timestamp', '>=', '2022-01-01'),]), # changes time field
        ('to_', '2022-01-01',
            [('utc_timestamp', '<=', '2022-01-01'),]), # changes time field
        ('downloaded_from', '2022-01-01',
            [('create_at', '>=', '2022-01-01'),]),
        ('downloaded_to', '2022-01-01',
            [('create_at', '<=', '2022-01-01'),]),
    ])
    async def test__build_query__erp_timescale_model__with_single_parameter(self, parameter, value, expected):
        await self.assert_build_erp_query({ parameter: value}, expected, TgCchF1)

    # Build queries for Mongo curves

    async def assert_build_mongo_query(self, filters, expected_query):
        filters = dict(filters)
        filters.setdefault("type", 'tg_cchfact')
        model = cch_model(filters['type'])
        query = await model.build_query(filters)
        assert query == expected_query

    async def test__build_query__mongo_model__no_filters(self):
        await self.assert_build_mongo_query(dict(), {})

    @pytest.mark.parametrize('parameter,value,expected', [
        ('cups', '12345678901234567890_this_should_disappear',
            {'name': {'$regex': '^12345678901234567890'}}),
        ('from_', '2022-01-01',
            {'datetime': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('to_', '2022-01-01',
            {'datetime': {'$lte': datetime.datetime(2022, 1, 2, 0, 0)}}),
        ('downloaded_from', '2022-01-01',
            {'create_at': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('downloaded_to', '2022-01-01',
            {'create_at': {'$lte': datetime.datetime(2022, 1, 1, 0, 0)}}),
        ('type', 'P1',
            {'type': {'$eq': 'p'}}),
        ('type', 'P2',
            {'type': {'$eq': 'p4'}}),
    ])
    async def test__build_query__mongo_model__with_single_parameter(self, parameter, value, expected):
        await self.assert_build_mongo_query({ parameter: value}, expected)

    async def test__build_query__mongo_model__with_several_parameters(self):
        cups = "a_cups"
        await self.assert_build_mongo_query(dict(
            cups = cups,
            **{'from_': '2022-01-01'}
        ),{
            'datetime': {'$gte': datetime.datetime(2022, 1, 1, 0, 0)},
            'name': {'$regex': '^a_cups'},
        })

    async def test__build_query__mongo_model__with_from_and_to(self):
        await self.assert_build_mongo_query({
            'from_': '2022-01-01',
            'to_': '2022-01-02',
        },{
            'datetime': {
                # Both conditions on datetime are joined
                '$gte': datetime.datetime(2022, 1, 1, 0, 0),
                '$lte': datetime.datetime(2022, 1, 3, 0, 0),
            },
        })

    async def test__build_query__mongo_model__with_downloaded_from_and_to(self):
        await self.assert_build_mongo_query({
            'downloaded_from': '2022-01-01',
            'downloaded_to': '2022-01-02',
        },{
            'create_at': {
                # Both conditions on datetime are joined
                '$gte': datetime.datetime(2022, 1, 1, 0, 0),
                '$lte': datetime.datetime(2022, 1, 2, 0, 0),
            },
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
            "ai": 6,
            "aiquality": 0,
            "ao": 0,
            "aoQuality": 0,
            "date": "2018-10-31 23:00:00+0000",
            "dateDownload": "2018-12-12 19:19:17",
            "dateUpdate": "2018-12-12 19:19:17",
            "measureType": 11,
            "r1": 0,
            "r1Quality": 0,
            "r2": 0,
            "r2Quality": 0,
            "r3": 0,
            "r3Quality": 0,
            "r4": 0,
            "r4Quality": 0,
            "reserve1": 0,
            "reserve1Quality": 0,
            "reserve2": 0,
            "reserve2Quality": 0,
            "season": 0,
            "source": 1,
            "type": "p",
            "validated": False,
        }

    async def test__get_P2_measurements(self, p2_id, app):
        p2 = await TgCchP1.create(p2_id)
        measurements = p2.measurements
        assert measurements == {
            "ai": 0,
            "aiquality": 0,
            "ao": 42,
            "aoQuality": 0,
            "date": "2017-01-31 22:00:00+0000",
            "dateDownload": "2019-11-29 05:21:50",
            "dateUpdate": "2020-02-04 15:12:38",
            "measureType": 11,
            "r1": 0,
            "r1Quality": 0,
            "r2": 2,
            "r2Quality": 0,
            "r3": 0,
            "r3Quality": 0,
            "r4": 0,
            "r4Quality": 0,
            "reserve1": 0,
            "reserve1Quality": 128,
            "reserve2": 0,
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


