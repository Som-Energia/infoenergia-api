from .base import *

# ERP configuration
ERP_CONF = env.json("ERP_CONF")

# Transport Pool configuration
TRANSPORT_POOL_CONF = env.json("TRANSPORT_POOL_CONF")

# ERP database, direct access skipping ERP
ERP_DB_CONF = env.json("ERP_DB_CONF")

# Mongo configuration
MONGO_CONF = env.str("MONGO_CONF")

# DATABASE configuration
DB_CONF = env.json("DATABASE_CONF")

# Redis configuration
REDIS_CONF = env.str("REDIS_CONF")

MAX_THREADS = 10

INVITATION_EXP_DAYS = 1

SANIC_JWT_SECRET = SECRET_KEY

RESULTS_TTL = env.int("RESULTS_TTL")

DATA_DIR = BASE_DIR
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
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
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
