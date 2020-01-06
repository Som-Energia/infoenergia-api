from datetime import datetime, timedelta

import jwt
from passlib.hash import pbkdf2_sha256
from pony.orm import db_session, select, core, commit
from sanic.exceptions import InvalidUsage
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt import exceptions, BaseEndpoint

from .models import InvitationToken, get_user, User

async def authenticate(request):
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
