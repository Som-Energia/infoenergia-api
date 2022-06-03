import os
import pyexpat
from unittest.mock import AsyncMock

import fakeredis
import nest_asyncio
import pytest
import yaml
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import pbkdf2_sha256
from pony.orm import commit, db_session
from sanic_testing import TestManager

from infoenergia_api.api.registration.models import User
from infoenergia_api.beedata_api import BeedataApiClient
from infoenergia_api.contrib.reports import Beedata

nest_asyncio.apply()


@pytest.fixture
def app():
    from infoenergia_api.app import app

    app.ctx.redis = fakeredis.FakeStrictRedis()
    app.ctx.mongo_client = AsyncIOMotorClient(app.config.MONGO_CONF)
    yield app
    app.ctx.mongo_client.close()
    app.ctx.thread_pool.shutdown()


@pytest.fixture
async def bapi(app):
    bapi = await BeedataApiClient.create(
        url=app.config.BASE_URL,
        username=app.config.USERNAME,
        password=app.config.PASSWORD,
        company_id=app.config.COMPANY_ID,
        cert_file=app.config.CERT_FILE,
        cert_key=app.config.KEY_FILE
    )
    bapi.login()
    yield bapi
    bapi.logout()


@pytest.fixture
async def beedata(bapi, app):
    beedata = Beedata(bapi, app.ctx.mongo_client, app.ctx.redis)
    yield beedata


@pytest.fixture
@db_session
def user():
    user = User.get(username='someone')
    if not user:
        user = User(
            username='someone',
            password=pbkdf2_sha256.hash('password'),
            email='someone@foo.bar',
            id_partner=1,
            is_superuser=True,
            category='partner'
        )
        commit()
    user._clear_psw = 'password'
    yield user
    user.delete()


@pytest.fixture()
def client(app):
    client = TestManager(app).test_client
    return client


@pytest.fixture
def async_client(app):
    client = TestManager(app).asgi_client
    return client


@pytest.fixture
async def auth_token(app, user):
    auth_body = {
        'username': user.username,
        'password': user._clear_psw,
    }
    _, response = await app.asgi_client.post('/auth', json=auth_body)
    token = response.json.get('access_token', None)
    return token


@pytest.fixture
def scenarios(app):
    with open(os.path.join(app.config.BASE_DIR, 'tests/json4test.yaml')) as f:
        scenarios = yaml.safe_load(f.read())
    return scenarios


@pytest.fixture
def mock_process_reports(monkeypatch):
    async_mock = AsyncMock()
    monkeypatch.setattr(
        'infoenergia_api.contrib.reports.Beedata.process_reports',
        async_mock
    )
    return async_mock


@pytest.fixture
def mocked_next_cursor(monkeypatch):
    next_cursor_mock = 'N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0='
    monkeypatch.setattr(
        'infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor',
        next_cursor_mock
    )


@pytest.fixture
def f5d_id():
    return '5c2dd783cb2f477212c77abb'


@pytest.fixture
def f1_id():
    return '5e1d8d9612cd738e89bb3cfb'


@pytest.fixture
def p1_id():
     return '5e1d8dd112cd738e89bc42eb'


@pytest.fixture
def p2_id():
    return '5e3011f912cd738e8991aca7'