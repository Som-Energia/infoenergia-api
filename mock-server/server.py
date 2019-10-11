import os

import connexion
from connexion.decorators.security import validate_scope
from connexion.exceptions import OAuthScopeProblem


BASE_DIR = os.path.dirname(os.path.abspath(__name__))



def basic_auth(username, password):
    if username == 'admin' and password == 'secret':
        info = {'sub': 'admin', 'scope': 'secret'}
    elif username == 'foo' and password == 'bar':
        info = {'sub': 'user1', 'scope': ''}
    else:
        # optional: raise exception for custom error response
        return None

    return info


if __name__ == '__main__':
    app = connexion.FlaskApp(
        __name__,
        specification_dir=os.path.join(BASE_DIR, 'docs/'),
        debug=True,

    )
    app.add_api('infoenergia-api.yaml', validate_responses=True)
    app.run(port=8090)
