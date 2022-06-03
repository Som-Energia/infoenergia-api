import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

from concurrent import futures
from unittest import TestCase, IsolatedAsyncioTestCase
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web

import fakeredis
import yaml
from passlib.hash import pbkdf2_sha256
from pony.orm import commit, db_session
from sanic_testing import TestManager

from infoenergia_api.api.registration.models import User


class BaseTestCaseAsync(AioHTTPTestCase):

    async def setUpAsync(self):
        from infoenergia_api import app
        await super().setUpAsync()
        self.app = app
        self.app.ctx.redis = fakeredis.FakeStrictRedis()

    async def get_application(self):
        self.app =  web.Application()
        return self.app


class BaseTestCase(IsolatedAsyncioTestCase):

    def setUp(self):
        from infoenergia_api import app
        self.app = app
        TestManager(self.app)

        self.client = app.test_client
        self.maxDiff = None
        if app.ctx.thread_pool._shutdown:
            app.ctx.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)

        with open(os.path.join(app.config.BASE_DIR, 'tests/json4test.yaml')) as f:
            self.json4test = yaml.safe_load(f.read())

    @db_session
    def get_or_create_user(self, username, password, email, partner_id, is_superuser, category):
        user = User.get(username=username)
        if not user:
            user = User(
                username=username,
                password=pbkdf2_sha256.hash(password),
                email=email,
                id_partner=partner_id,
                is_superuser=is_superuser,
                category=category
            )
            commit()
        return user

    @db_session
    def delete_user(self, user):
        user.delete()

    @db_session
    async def get_auth_token(self, username, password):
        auth_body = {
            'username': username,
            'password': password,
        }
        _, response = await self.client.post('/auth', json=auth_body)
        token = response.json.get('access_token', None)
        return token
