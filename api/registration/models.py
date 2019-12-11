import os

from passlib.hash import pbkdf2_sha256
from pony.orm import (Database, Optional, PrimaryKey, Required, commit,
                      db_session, set_sql_debug)

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

db = Database()

# set_sql_debug(True)


class User(db.Entity):
    _table_ = 'user'

    id = PrimaryKey(int, auto=True)
    username = Required(str)
    password = Required(str)
    id_partner = Optional(int)
    is_superuser = Required(bool)


db.bind(
    provider='sqlite',
    filename=os.path.join(BASE_DIR, 'SomInfoenergia.sqlite'),
    create_db=True
)
db.generate_mapping(create_tables=True)


def get_user(username):
    user = User.get(username=username)
    return user
