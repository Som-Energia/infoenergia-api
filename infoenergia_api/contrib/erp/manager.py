from erppeek import Client
from pool_transport import PoolTransport

from config import config


class ERPManager:
    """
    Tiny class to manage erp connection to be accesible for any part of the code
    """

    _erp_con = None

    @classmethod
    def _erp_instance(cls) -> Client:
        if cls._erp_con is None:
            cls._erp_con = Client(
                transport=PoolTransport(secure=config.TRANSPORT_POOL_CONF["secure"]),
                **config.ERP_CONF,
            )

        return cls._erp_con


def get_erp_instance() -> Client:
    return ERPManager._erp_instance()
