import asyncio

from config import config
from infoenergia_api.contrib import BeedataApiClient


class BeedataApiManager(object):
    _bapi = None

    @classmethod
    def get_instance(cls):
        if cls._bapi is None:
            cls._bapi = asyncio.run(BeedataApiClient.create(
            url=config.BASE_URL,
            username=config.USERNAME,
            password=config.PASSWORD,
            company_id=config.COMPANY_ID,
            cert_file=config.CERT_FILE,
            cert_key=config.KEY_FILE
        ))
        return cls._bapi


class BeedataApiMixin(object):

    @property
    def bapi(self):
        return BeedataApiManager.get_instance()

