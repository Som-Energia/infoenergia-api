import os
import pathlib

from environs import Env

env = Env()
env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Supermega secret key
SECRET_KEY = '1234'

# Max threads in pool
MAX_THREADS = 5

# Response timeout
RESPONSE_TIMEOUT = 36000
