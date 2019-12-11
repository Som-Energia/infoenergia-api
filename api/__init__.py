from sanic import Sanic
from sanic.log import logger
from sanic_jwt import Initialize, exceptions

from .contracts import bp_contracts
from .registration.login import authenticate

app = Sanic(__name__)
Initialize(app, authenticate=authenticate)
app.blueprint(bp_contracts)
