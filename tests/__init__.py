import os
os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.testing')

from sanic.log import logger

settings = os.environ.get('INFOENERGIA_MODULE_SETTINGS')

logger.warning(f'You are runnig test with {settings} settings!!')