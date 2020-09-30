from datetime import datetime, timedelta

import jwt
from passlib.hash import pbkdf2_sha256
from pony.orm import commit, core, db_session, select
from sanic.exceptions import InvalidUsage
from sanic.log import logger
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt import BaseEndpoint, exceptions

from .models import InvitationToken, User, get_user


async def authenticate(request):
    body = request.json
    username = body.get('username', '')
    password = body.get('password', '')

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")

    user = get_user(username)

    if user and pbkdf2_sha256.verify(password, user.password):
        logger.info('user: %s', user.username)
        return user

    raise exceptions.AuthenticationFailed("Wrong user name or password")


class InvitationUrlToken(HTTPMethodView):

    async def get(self, request):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=request.app.config.INVITATION_EXP_DAYS)
        }
        payload['is_superuser'] = request.args.get('is_superuser', False)
        payload['id_partner'] = request.args.get('id_partner')
        payload['category'] = request.args.get('category')

        with db_session:
            invitation_token = InvitationToken(
                inv_token=jwt.encode(
                    payload, request.app.config.SECRET_KEY, algorithm='HS256'
                ).decode(),
                used=False
            )

        url = '{}://{}{}?invitation_token={}'.format(
            request.scheme,
            request.host,
            request.app.url_for('auth_bp.Register'),
            invitation_token.inv_token
        )
        return json(url)


class Register(BaseEndpoint):

    async def post(self, request):
        invitation_token = request.args.get('invitation_token')
        if not invitation_token:
            return json(
                {'exception': 'Invalid usage',
                 'reasons': ['Invitation token not provided']
                },
                status=400
            )
        try:
            with db_session:
                token = select(
                    token
                    for token in InvitationToken
                    if token.inv_token == invitation_token and token.used == False
                ).first()
                if not token:
                    return json(
                        {'exception': 'Invalid token',
                         'reasons': ['Invitation token has been expired or is not valid']
                        },
                        status=400
                    )
                try:
                    payload = jwt.decode(
                        invitation_token, request.app.config.SECRET_KEY
                    )
                except jwt.ExpiredSignatureError as e:
                    return json(
                        {'exception': 'Invalid token',
                         'reasons': ['Invitation has expired or is not valid']
                        },
                        status=400
                    )
                body = request.json
                user = User(
                    username=body['username'],
                    password=pbkdf2_sha256.hash(body['password']),
                    email=body['email'],
                    id_partner=payload.get('id_partner'),
                    category=payload.get('category'),
                    is_superuser=payload.get('is_superuser', False)
                )
                commit()
                token.used = True
                result = user.to_dict()
        except core.TransactionIntegrityError as e:
            return json(
                {'exception': 'User exception',
                 'reasons': ['It\'s possible your user already exists']
                },
                status=400
            )

        return json(result)


extra_views = (
    ('/register', Register),
)
