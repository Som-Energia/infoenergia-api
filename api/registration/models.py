from pony.orm import Database, Optional, PrimaryKey, Required, db_session

db = Database()


class InvitationToken(db.Entity):
    _table_  = 'invitation_tokens'

    id = PrimaryKey(int, auto=True)

    inv_token = Required(str)

    used = Required(bool)


class User(db.Entity):
    _table_ = 'user'

    id = PrimaryKey(int, auto=True)

    username = Required(str, unique=True)

    password = Required(str)

    email = Required(str)

    id_partner = Optional(int)

    is_superuser = Required(bool)

    def to_dict(self):
        attrs = ['id', 'username', 'email', 'id_partner', 'is_superuser']
        return {
            attr: getattr(self, attr, None)
            for attr in attrs
        }


@db_session
def get_user(username):
    user = User.get(username=username)
    return user
