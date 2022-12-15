from passlib.hash import pbkdf2_sha256
from pony.orm import db_session
from sanic_jwt import exceptions

from tests.base import BaseTestCase, User

class TestLogin(BaseTestCase):
    @db_session
    async def test__authenticate_user(self):
        user = User(
            username="someone",
            password=pbkdf2_sha256.hash(self.dummy_passwd),
            email="someone@somenergia.coop",
            id_partner=1,
            is_superuser=True,
            category="partner",
        )
        auth_body = {
            "username": user.username,
            "password": self.dummy_passwd,
        }

        _, response = await self.client.post("/auth", json=auth_body)
        token = response.json.get("access_token", None)

        self.assertIsNotNone(token)
        user.delete()

    @db_session
    async def test__authenticate_failed(self):
        auth_body = {
            "username": "no_one",
            "password": self.dummy_passwd,
        }

        _, response = await self.client.post("/auth", json=auth_body)
        self.assertRaises(exceptions.AuthenticationFailed)

    @db_session
    async def test__authenticate_missing_username(self):
        auth_body = {
            "username": "",
            "password": self.dummy_passwd,
        }

        _, response = await self.client.post("/auth", json=auth_body)
        self.assertRaises(exceptions.AuthenticationFailed)
