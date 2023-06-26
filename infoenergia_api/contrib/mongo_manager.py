from config import config
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio


def get_mongo_instance():
    self = get_mongo_instance
    current_loop = asyncio.get_running_loop()
    if hasattr(self, "loop") and not self.loop.is_running():
        print("Renewing the mongo client because loop has changed")
        del self.loop
        if hasattr(self, "instance"):
            self.instance.close()
            del self.instance
    self.loop = current_loop
    if not hasattr(self, "instance"):
        self.instance = AsyncIOMotorClient(config.MONGO_CONF, io_loop=current_loop)
    return self.instance
