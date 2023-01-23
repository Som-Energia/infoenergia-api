__version__ = VERSION = "2.1.0"

import os
from concurrent import futures

import aioredis
import sentry_sdk
from erppeek import Client
from motor.motor_asyncio import AsyncIOMotorClient
from pony.orm.core import BindingError
from pool_transport import PoolTransport
from sanic import Sanic
from sanic.log import logger
from sanic.signals import Event
from sanic_jwt import Initialize as InitializeJWT
from sanic_jwt.exceptions import AuthenticationFailed, Unauthorized
from sentry_sdk.integrations.sanic import SanicIntegration

from . import VERSION
from .api.cch import bp_cch_measures
from .api.contracts import bp_contracts
from .api.f1_measures import bp_f1_measures
from .api.modcontracts import bp_modcontracts
from .api.registration.models import retrieve_user
from .api.registration.utils import ApiAuthResponses
from .api.registration.views import InvitationUrlToken, authenticate, extra_views
from .api.reports import bp_reports
from .api.tariff import bp_tariff
from .api.utils import get_db_instance
from .contrib.mixins import ResponseMixin
from .contrib.erp import get_erp_instance


def attach_signals(app: Sanic):
    @app.signal(Event.SERVER_INIT_BEFORE)
    async def server_init(app, loop):
        app.ctx.redis = aioredis.from_url(app.config.REDIS_CONF)
        app.ctx.mongo_client = AsyncIOMotorClient(app.config.MONGO_CONF, io_loop=loop)

    @app.signal(Event.SERVER_SHUTDOWN_AFTER)
    async def shutdown_app(app, loop):
        logger.info("Shuting down api... ")
        app.ctx.mongo_client.close()
        app.ctx.thread_pool.shutdown()

    @app.exception(AuthenticationFailed, Unauthorized)
    async def unauthorized_errors(request, exception):
        return ResponseMixin.unauthorized_error_response(exception)

    @app.exception(Exception)
    async def unexpected_errors(request, exception):
        return ResponseMixin.unexpected_error_response(exception)

    @app.signal(Event.HTTP_LIFECYCLE_EXCEPTION)
    async def http_lifecycle_handle_handler(request, exception):
        if hasattr(request.ctx, "user"):
            sentry_sdk.set_user(
                {"username": request.ctx.user.username, "email": request.ctx.user.email}
            )

    @app.signal(Event.HTTP_LIFECYCLE_COMPLETE)
    async def http_lifecycle_comple_handler(conn_info):
        sentry_sdk.set_user(None)


def initialize_plugins(app: Sanic):
    InitializeJWT(
        app,
        authenticate=authenticate,
        retrieve_user=retrieve_user,
        class_views=extra_views,
        responses_class=ApiAuthResponses,
    )


def attach_bluprints_and_routes(app: Sanic):
    app.blueprint(bp_contracts)
    app.blueprint(bp_f1_measures)
    app.blueprint(bp_modcontracts)
    app.blueprint(bp_cch_measures)
    app.blueprint(bp_reports)
    app.blueprint(bp_tariff)

    app.add_route(
        InvitationUrlToken.as_view(), "/auth/invitationtoken", host="localhost:9000"
    )


def attach_context(app: Sanic):
    app.ctx.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)

    app.ctx.erp_client = get_erp_instance()
    db = get_db_instance()

    try:
        db.bind(
            provider="sqlite",
            filename=os.path.join(
                app.config.DATA_DIR, "{}.sqlite3".format(app.config.DB_CONF["database"])
            ),
            create_db=True,
        )
        db.generate_mapping(create_tables=True)
    except BindingError:
        pass
    app.ctx.db = db


def build_app(app_name: str) -> Sanic:
    from config import config

    app = Sanic(name=app_name)

    ## Triki if until https://github.com/sanic-org/sanic/pull/2451 is resolved
    if (
        environment := os.environ.get("INFOENERGIA_MODULE_SETTINGS").split(".")[-1]
        != "testing"
    ):
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            integrations=[SanicIntegration()],
            release=VERSION,
            environment=environment,
        )

    try:
        app.update_config(config)
        initialize_plugins(app)
        attach_bluprints_and_routes(app)
        attach_signals(app)
        attach_context(app)
    except Exception as e:
        msg = "An error ocurred building Infoenergia API: %s"
        logger.exception(msg, str(e))
        raise e
    else:
        logger.info("Build api finished")
        return app
