from config import config
from motor.motor_asyncio import AsyncIOMotorClient

def get_mongo_instance():
    if not hasattr(get_mongo_instance, 'instance'):
        get_mongo_instance.instance = AsyncIOMotorClient(config.MONGO_CONF)
    return get_mongo_instance.instance

