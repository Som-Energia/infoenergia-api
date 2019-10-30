from sanic import Sanic

from .contracts import bp_contracts

app = Sanic(__name__)
app.blueprint(bp_contracts)
