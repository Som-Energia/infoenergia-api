import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

from concurrent import futures
from unittest import TestCase
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

import fakeredis

import yaml
from passlib.hash import pbkdf2_sha256
from pony.orm import commit, db_session

from infoenergia_api import app
from infoenergia_api.api.registration.models import User

class BaseTestCaseAsync(AioHTTPTestCase):

    async def setUpAsync(self):
        await super().setUpAsync()
        self.app = app
        self.app.redis = fakeredis.FakeStrictRedis()

    async def get_application(self):
        self.app =  web.Application()
        return self.app


class BaseTestCase(TestCase):

    def setUp(self):
        self.app = app
        self.app.test_mode = True
 
        self.client = app.test_client 
        self.maxDiff = None
        if app.thread_pool._shutdown:
            app.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)

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
    def get_auth_token(self, username, password):
        auth_body = {
            'username': username,
            'password': password,
        }
        _, response = self.client.post('/auth', json=auth_body)
        token = response.json.get('access_token', None)
        return token
