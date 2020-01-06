import os
from importlib import import_module
from api.exceptions import ImproperlyConfigured

ENVIRONMENT_VARIABLE = 'INFOENERGIA_MODULE_SETTINGS'

os.environ.setdefault('INFOENERGIA_MODULE_SETTINGS', 'config.settings.devel')


class Settings(object):

    def __init__(self, settings_module):
        self.SETTINGS_MODULE = settings_module
        if not self.SETTINGS_MODULE:
            msg = 'Environment variable \"{}\" is not set'
            raise ImproperlyConfigured(msg.format(ENVIRONMENT_VARIABLE))

        mod = import_module(self.SETTINGS_MODULE)
        for setting in dir(mod):
            if setting.isupper():
                setattr(self, setting, getattr(mod, setting))


config = Settings(os.getenv(ENVIRONMENT_VARIABLE))


def configure_logging(logging_config):
    from logging.config import dictConfig

    dictConfig(logging_config)
