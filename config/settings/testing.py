import os
from .base import *

test_env = Env()
test_env.read_env(os.path.join(BASE_DIR, "tests/.env.test"), override=True)

ERP_CONF = test_env.json("ERP_CONF")

# Transport Pool configuration
TRANSPORT_POOL_CONF = env.json("TRANSPORT_POOL_CONF")

# ERP database, direct access skipping ERP
ERP_DB_CONF = env.json("ERP_DB_CONF")

MONGO_CONF = test_env.str("MONGO_CONF")

DB_CONF = test_env.json("DATABASE_CONF")

# Redis configuration
REDIS_CONF = env.str("REDIS_CONF")

MAX_THREADS = 10

DATA_DIR = BASE_DIR

SANIC_JWT_SECRET = SECRET_KEY

INVITATION_EXP_DAYS = 1

RECORD_MODE = os.environ.get("RECORD_MODE", "new_episodes")


USE_UVLOOP = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] [%(process)d] [%(levelname)s]"
            "[%(module)s.%(funcName)s:%(lineno)s] %(message)s"
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/infoenergia-api_test.log",
            "maxBytes": 5 * (1024 * 1024),
            "backupCount": 7,
            "formatter": "verbose",
        }
    },
    "loggers": {
        "api": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
    },
}

# Access BeeData API:
CERT_FILE = env.str("CERT_FILE")
KEY_FILE = env.str("KEY_FILE")
COMPANY_ID = env.int("COMPANY_ID")
BASE_URL = env.str("BASE_URL")
APIVERSION = env.str("APIVERSION")
USERNAME = env.str("USERNAME")
PASSWORD = env.str("PASSWORD")

# Number of workers for process Reports
N_WORKERS = env.int("N_WORKERS")

CURVE_TYPE_DEFAULT_BACKEND = env.str('CURVE_TYPE_DEFAULT_BACKEND', CURVE_TYPE_DEFAULT_BACKEND)
CURVE_TYPE_BACKENDS = env.json('CURVE_TYPE_BACKENDS', json.dumps(CURVE_TYPE_BACKENDS))
