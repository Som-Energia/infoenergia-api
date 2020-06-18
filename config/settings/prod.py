from .base import *

# ERP configuration
ERP_CONF = env.json('ERP_CONF')

# DATABASE configuration
DB_CONF = env.json('DATABASE_CONF')

# Redis configuration
REDIS_CONF = env.str('REDIS_CONF')

ACCESS_LOG = False

PROXIES_COUNT = 1

MAX_THREADS = env.int('MAX_THREADS')

INVITATION_EXP_DAYS = env.int('EXP_DAYS')

SECRET_KEY = env.str('SECRET_KEY')

SANIC_JWT_SECRET = SECRET_KEY
SANIC_JWT_EXPIRATION_DELTA = env.int('JWT_EXPIRATION_DELTA') * 48

RESULTS_TTL = env.int('RESULTS_TTL') * 18

DATA_DIR = env.str('DATA_DIR')

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
