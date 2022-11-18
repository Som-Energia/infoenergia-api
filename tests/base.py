import asyncio
import os
import string
import secrets

os.environ.setdefault("INFOENERGIA_MODULE_SETTINGS", "config.settings.testing")

from concurrent import futures
from unittest import TestCase

import yaml
from passlib.hash import pbkdf2_sha256
from pony.orm import commit, db_session
from sanic_testing import TestManager
from infoenergia_api.api.registration.models import User


class BaseTestCase(TestCase):
    def setUp(self):
        from infoenergia_api import build_app

        self.app = build_app("infoenergia-api-test")
        self.client = TestManager(self.app).asgi_client
        self.maxDiff = None
        if self.app.ctx.thread_pool._shutdown:
            self.app.ctx.thread_pool = futures.ThreadPoolExecutor(
                self.app.config.MAX_THREADS
            )

        self.loop = asyncio.get_event_loop()

        with open(os.path.join(self.app.config.BASE_DIR, "tests/json4test.yaml")) as f:
            self.json4test = yaml.safe_load(f.read())

    @db_session
    def get_or_create_user(
        self, username, password, email, partner_id, is_superuser, category
    ):
        user = User.get(username=username)
        if not user:
            user = User(
                username=username,
                password=pbkdf2_sha256.hash(password),
                email=email,
                id_partner=partner_id,
                is_superuser=is_superuser,
                category=category,
            )
            commit()
        return user

    @db_session
    def delete_user(self, user):
        user.delete()

    @db_session
    def get_auth_token(self, username, password):
        auth_body = {
            "username": username,
            "password": password,
        }
        _, response = self.loop.run_until_complete(
            self.client.post("/auth", json=auth_body)
        )
        token = response.json.get("access_token", None)
        return token

    dummy_passwd = "".join(secrets.choice(string.ascii_letters) for i in range(8))
