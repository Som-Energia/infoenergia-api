from pony.orm import Database


class DbManager:
    _db = None

    @classmethod
    def _db_instance(cls):
        if cls._db is None:
            cls._db = Database()
        return cls._db


def get_db_instance():
    return DbManager._db_instance()
