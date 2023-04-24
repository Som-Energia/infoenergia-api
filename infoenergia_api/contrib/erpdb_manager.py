from config import config
from psycopg import AsyncConnection


async def get_erpdb_instance():
    f = get_erpdb_instance
    if not hasattr(f, 'instance'):
        f.instance = await AsyncConnection.connect(**config.ERP_DB_CONF)
    return f.instance


