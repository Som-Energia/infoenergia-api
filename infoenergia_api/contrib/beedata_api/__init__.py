from config import config

from .client import BeedataApiClient


class BeedataApiManager(object):
    _bapi = None

    @classmethod
    async def get_instance(cls):
        if cls._bapi is None:
            cls._bapi = await BeedataApiClient.create(
                url=config.BASE_URL,
                username=config.USERNAME,
                password=config.PASSWORD,
                company_id=config.COMPANY_ID,
                cert_file=config.CERT_FILE,
                cert_key=config.KEY_FILE,
            )
        return cls._bapi


class BeedataApiMixin(object):
    @property
    async def bapi(self):
        return await BeedataApiManager.get_instance()
