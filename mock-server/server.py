import os
import time

import connexion
from connexion.decorators.security import validate_scope
from connexion.exceptions import OAuthScopeProblem

from jose import JWTError, jwt

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

JWT_ISSUER = 'com.zalando.connexion'
JWT_SECRET = 'change_this'
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'

def basic_auth(username, password):
    if username == 'admin' and password == 'secret':
        timestamp = _current_timestamp()
        payload = {
            "iss": JWT_ISSUER,
            "iat": int(timestamp),
            "exp": int(timestamp + JWT_LIFETIME_SECONDS),
            "sub": str(username),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    else:
        # optional: raise exception for custom error response
        return None


def _current_timestamp() -> int:
    return int(time.time())



if __name__ == '__main__':
    app = connexion.FlaskApp(
        __name__,
        specification_dir=os.path.join(BASE_DIR, 'docs/'),
        debug=True,

    )
    app.add_api('infoenergia-api.yaml', validate_responses=True)
    app.run(port=8090)
