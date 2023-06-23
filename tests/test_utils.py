import asyncio
from erppeek import Client
from motor.motor_asyncio import AsyncIOMotorClient
from pony.orm import db_session

from infoenergia_api.utils import get_contract_id
from config import config
from tests.base import BaseTestCase

from infoenergia_api.api.utils import get_db_instance


def test__get_db_instance():
    db = get_db_instance()

    db2 = get_db_instance()

    assert db is db2


class TestUtils(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.erp = Client(**config.ERP_CONF)
        self.app.ctx.mongo_client = AsyncIOMotorClient(config.MONGO_CONF)
        self.loop = asyncio.get_event_loop()
        self.f5d_cups = self.json4test["a_valid_f5d_cups"]

    @db_session
    def test__valid_contract(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=True,
            category="partner",
        )
        valid = get_contract_id(self.erp, self.f5d_cups, user)
        self.assertTrue(valid)
        self.delete_user(user)

    @db_session
    def test__valid_contract_without_permission(self):
        user = self.get_or_create_user(
            username="someone",
            password=self.dummy_passwd,
            email="someone@somenergia.coop",
            partner_id=1,
            is_superuser=False,
            category="Energética",
        )
        invalid = get_contract_id(self.erp, self.f5d_cups, user)
        self.assertFalse(invalid)
        self.delete_user(user)
