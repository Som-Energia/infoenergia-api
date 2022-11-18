import os
from unittest.mock import AsyncMock

import fakeredis
import nest_asyncio
import pytest
import yaml
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import pbkdf2_sha256
from pony.orm import commit, db_session
from sanic_testing import TestManager

from config import config
from infoenergia_api.api.registration.models import User
from infoenergia_api.contrib.beedata_api import BeedataApiManager

# For nesting asyncio loops
nest_asyncio.apply()


@pytest.fixture
def app():
    """
    Returns an instance of Inforenergia api app
    """
    from infoenergia_api import build_app

    app = build_app("infoenergia-api-test")

    app.ctx.redis = fakeredis.FakeStrictRedis()
    app.ctx.mongo_client = AsyncIOMotorClient(app.config.MONGO_CONF)
    yield app
    app.ctx.mongo_client.close()
    app.ctx.thread_pool.shutdown()


@pytest.fixture
async def bapi():
    """
    Return an instance of Beedata api client
    """
    bapi = await BeedataApiManager.get_instance()
    yield bapi
    bapi.__del__()
    BeedataApiManager._bapi = None


@pytest.fixture
@db_session
def user():
    """
    Return an instance of an inforenergia api user
    """
    user = User.get(username="someone")
    if not user:
        user = User(
            username="someone",
            password=pbkdf2_sha256.hash("password"),
            email="someone@foo.bar",
            id_partner=1,
            is_superuser=True,
            category="partner",
        )
        commit()
    user._clear_psw = "password"
    yield user
    user.delete()


@pytest.fixture
def client(app):
    """
    Returns an instance of a test client
    """
    client = TestManager(app).test_client
    return client


@pytest.fixture
def async_client(app):
    """
    Returns an instasnce of an async test client
    """
    client = TestManager(app).asgi_client
    return client


@pytest.fixture
async def auth_token(app, user):
    """
    Returns a valid infoenergia api auth token
    """
    auth_body = {
        "username": user.username,
        "password": user._clear_psw,
    }
    _, response = await app.asgi_client.post("/auth", json=auth_body)
    token = response.json.get("access_token", None)
    return token


@pytest.fixture
def scenarios(app):
    """
    Returns a set of scenarios to test
    """
    with open(os.path.join(app.config.BASE_DIR, "tests/json4test.yaml")) as f:
        scenarios = yaml.safe_load(f.read())
    return scenarios


@pytest.fixture
def mock_process_reports(monkeypatch):
    """
    Returns a process_reports mocked function
    """
    async_mock = AsyncMock()
    monkeypatch.setattr(
        "infoenergia_api.contrib.reports.BeedataReports.process_reports", async_mock
    )
    return async_mock


@pytest.fixture
def mocked_next_cursor(monkeypatch):
    """
    Returns a mocked cursor
    """

    async def next_cursor_mock(self, request_id, next_cursor):
        return "N2MxNjhhYmItZjc5Zi01MjM3LTlhMWYtZDRjNDQzY2ZhY2FkOk1RPT0="

    monkeypatch.setattr(
        "infoenergia_api.contrib.pagination.PaginationLinksMixin._next_cursor",
        next_cursor_mock,
    )


@pytest.fixture
def f5d_id():
    """
    Returns a random f5d curve id
    """
    return "5c2dd783cb2f477212c77abb"


@pytest.fixture
def f1_id():
    """
    Returns a random f1 curve id
    """
    return "5e1d8d9612cd738e89bb3cfb"


@pytest.fixture
def p1_id():
    """
    Returns a random p1 curve id
    """
    return "5e1d8dd112cd738e89bc42eb"


@pytest.fixture
def p2_id():
    """
    Returns a random p2 curve id
    """
    return "5e3011f912cd738e8991aca7"


@pytest.fixture
def beedata_api_correct_credentials():
    """
    Returns a dictionary with correct beedata api credentials
    """
    return dict(
        url=config.BASE_URL,
        username=config.USERNAME,
        password=config.PASSWORD,
        company_id=config.COMPANY_ID,
        cert_file=config.CERT_FILE,
        cert_key=config.KEY_FILE,
    )


@pytest.fixture
def beedata_api_bad_credentials():
    """
    Returns a dictionary with incorrect beedata api credentials
    """
    return dict(
        url=config.BASE_URL,
        username="erdtfy1253",
        password=config.PASSWORD,
        company_id=config.COMPANY_ID,
        cert_file=config.CERT_FILE,
        cert_key=config.KEY_FILE,
    )
