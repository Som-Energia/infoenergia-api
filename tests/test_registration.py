import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

from passlib.hash import pbkdf2_sha256
from pony.orm import db_session

from api.registration.models import User

from .base import BaseTestCase


class TestLogin(BaseTestCase):

    @db_session
    def test__authenticate_user(self):
        user = User(
            username='someone',
            password=pbkdf2_sha256.hash("12341234"),
            email='someone@somenergia.coop',
            id_partner=1,
            is_superuser=True
        )
        auth_body = {
            'username': user.username,
            'password': "12341234",
        }

        _, response = self.client.post('/auth', json=auth_body)
        token = response.json.get('access_token', None)

        self.assertIsNotNone(token)
        user.delete()
