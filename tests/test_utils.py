import asyncio
from erppeek import Client
from motor.motor_asyncio import AsyncIOMotorClient
from pony.orm import db_session

from infoenergia_api.contrib.cch import Cch
from infoenergia_api.utils import get_contract_id, save_report, read_report
from config import config
from tests.base import BaseTestCase


class TestUtils(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.erp = Client(**config.ERP_CONF)
        self.app.mongo_client = AsyncIOMotorClient(config.MONGO_CONF)
        self.loop = asyncio.get_event_loop()
        self.f5d_id = '5c2dd783cb2f477212c77abb'

    @db_session
    def test__valid_contract(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=True,
            category='partner'
        )
        f5d = self.loop.run_until_complete(Cch.create(self.f5d_id, 'tg_cchfact'))
        valid = get_contract_id(self.erp, f5d.name, user)
        self.assertTrue(valid)
        self.delete_user(user)

    @db_session
    def test__valid_contract_without_permission(self):
        user = self.get_or_create_user(
            username='someone',
            password='123412345',
            email='someone@somenergia.coop',
            partner_id=1,
            is_superuser=False,
            category='Energética'
        )
        f5d = self.loop.run_until_complete(Cch.create(self.f5d_id, 'tg_cchfact'))
        invalid = get_contract_id(self.erp, f5d.name, user)
        self.assertFalse(invalid)
        self.delete_user(user)

    def test__insert_or_update_report(self):
        contractId = '12346'
        report = {'_items': [ {'report': 2, 'contractId': '12346'}] }
        reportId = self.loop.run_until_complete(
            save_report(report, contractId)
        )
        expectedReport = self.loop.run_until_complete(
            read_report(reportId)
        )
        self.assertEqual(report['_items'], expectedReport['_items'])
