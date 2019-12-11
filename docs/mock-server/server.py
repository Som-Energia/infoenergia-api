import os
import time

import connexion
import six
import yaml
from connexion.mock import MockResolver
from jose import JWTError, jwt
from werkzeug.exceptions import Unauthorized

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

with open(os.path.join(BASE_DIR, 'tests/json4test.yaml')) as f:
    json4test = yaml.load(f.read())


JWT_ISSUER = 'som-energia'
JWT_SECRET = 'j4h5gf6d78RFJTHGYH(/&%$·sdgfh'
JWT_LIFETIME_SECONDS = 1600
JWT_ALGORITHM = 'HS256'

tokens = {}


def basic_auth(username, password):
    if username == 'admin' and password == 'secret':
        timestamp = _current_timestamp()
        payload = {
            "iss": JWT_ISSUER,
            "iat": int(timestamp),
            "exp": int(timestamp + JWT_LIFETIME_SECONDS),
            "sub": str(username),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        tokens[username] = token
        return token
    else:
        return ('Invalid credentials', 401)


def _current_timestamp():
    return int(time.time())


def decode_token(token):
    try:
        if token in tokens.values():
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        six.raise_from(Unauthorized, e)


def get_contract_by_id(user, token_info, contractId):
    return json4test['jsonContractById']


def get_contracts(user, token_info, limit, from_, to_, tariff, juridic_type):
    return json4test['jsonList'][:limit]


if __name__ == '__main__':
    api_extra_args = {}
    resolver = MockResolver(mock_all=False)
    api_extra_args['resolver'] = resolver

    app = connexion.FlaskApp(
        __name__,
        specification_dir=os.path.join(BASE_DIR, 'docs/'),
        debug=True,
    )
    app.add_api(
        'infoenergia-api.yaml',
        validate_responses=True,
        **api_extra_args
    )

    app.run(host='localhost', port=8090)
