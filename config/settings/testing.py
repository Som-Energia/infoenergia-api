from .base import *

test_env = Env()
test_env.read_env(os.path.join(BASE_DIR, 'tests'))

ERP_CONF = test_env.json('ERP_CONF')

DB_CONF = test_env.json('DATABASE_CONF')

MAX_THREADS = 10

SANIC_JWT_SECRET = SECRET_KEY
INVITATION_EXP_DAYS = 1

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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/infoenergia-api_test.log',
            'maxBytes': 5 * (1024 * 1024),
            'backupCount': 7,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'api': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
