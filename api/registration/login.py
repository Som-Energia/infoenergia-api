from passlib.hash import pbkdf2_sha256
from sanic.log import logger
from sanic_jwt import exceptions

from .models import get_user


async def authenticate(request, *args, **kwargs):
    body = request.json
    username = body.get('username', '')
    password = body.get('password', '')

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")

    user = get_user(username)

    if user and pbkdf2_sha256.verify(password, user.password):
        logger.info('user: {}'.format(user.username))
        return user

    raise exceptions.AuthenticationFailed("Wrong user name or password")
