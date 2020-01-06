from .base import *

ACCESS_LOG = False

PROXIES_COUNT = 1

MAX_THREADS = 20

INVITATION_EXP_DAYS = env.int('EXP_DAYS')

SECRET_KEY = env.str('SECRET_KEY')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(process)d] [%(levelname)s]'
                      '[%(module)s.%(funcName)s:%(lineno)s] %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/infoenergia-api.log',
            'when': 'midnight',
            'backupCount': 7,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'api': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        },
    }
}
