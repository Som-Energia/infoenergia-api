"""
Base and common settings for api configuration
"""
import os

from environs import Env

env = Env()
env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Supermega secret key
SECRET_KEY = "1234"

# Max threads in pool
MAX_THREADS = 200

# Max concurrent tasks
MAX_TASKS = 1

# I will wait until this timeout seconds
TASKS_TIMEOUT = 0.5

# Response timeout
RESPONSE_TIMEOUT = 36000

SANIC_JWT_USER_ID = "id"

SENTRY_DSN = env.str("SENTRY_DSN")

ERP_CURVES = env.list("ERP_CURVES", ["tg_f1", "tg_cchautoconsum", "tg_gennetabeta"])
