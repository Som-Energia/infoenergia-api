import os
import pathlib
import yaml

from environs import Env

env = Env()
env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ERP_CONF = env.json('ERP_CONF')

DB_CONF = env.json('DATABASE_CONF')

SECRET_KEY = '1234'
