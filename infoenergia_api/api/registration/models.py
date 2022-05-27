import enum
from pony.orm import Database, Optional, PrimaryKey, Required, db_session

db = Database()


class InvitationToken(db.Entity):
    _table_ = 'invitation_tokens'

    id = PrimaryKey(int, auto=True)

    inv_token = Required(str)

    used = Required(bool)


class UserCategory(enum.Enum):
    ADMIN = 'admin'

    PARTNER = 'partner'

    ENERGETICA = 'Energética'


class User(db.Entity):
    _table_ = 'user'

    id = PrimaryKey(int, auto=True)

    username = Required(str, unique=True)

    password = Required(str)

    email = Required(str)

    id_partner = Optional(int)

    category = Required(str)

    is_superuser = Required(bool)

    def to_dict(self):
        attrs = [
            'id', 'username', 'email', 'id_partner', 'is_superuser', 'category'
        ]
        return {
            attr: getattr(self, attr, None)
            for attr in attrs
        }

    def __repr__(self):
        return f"<User:{self.username}>"


@db_session
def get_user(username):
    user = User.get(username=username)
    return user


async def retrieve_user(request, payload, *args, **kwargs):
    if not payload:
        return None

    user_id = payload.get('id', None)
    with db_session:
        user = User.get(id=user_id)

    return user
