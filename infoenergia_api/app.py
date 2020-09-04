import os
from concurrent import futures

import aioredis
from erppeek import Client
from sanic import Sanic
from sanic.log import logger
from sanic_jwt import Initialize

from infoenergia_api.api.contracts import bp_contracts
from infoenergia_api.api.f1_measures import bp_f1_measures
from infoenergia_api.api.modcontracts import bp_modcontracts
from infoenergia_api.api.registration.login import (InvitationUrlToken,
                                                    authenticate, extra_views)
from infoenergia_api.api.registration.models import db
from infoenergia_api.api.tariff import bp_tariff


def build_app():
    from config import config
    app = Sanic('infoenergia-api')
    try:
        app.config.from_object(config)

        Initialize(app, authenticate=authenticate, class_views=extra_views)
        app.blueprint(bp_contracts)
        app.blueprint(bp_f1_measures)
        app.blueprint(bp_modcontracts)
        app.blueprint(bp_tariff)

        app.add_route(
            InvitationUrlToken.as_view(),
            '/auth/invitationtoken',
            host='localhost:9000'
        )

        app.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)
        app.erp_client = Client(**app.config.ERP_CONF)

        db.bind(
            provider='sqlite',
            filename=os.path.join(
                app.config.DATA_DIR,
                '{}.sqlite3'.format(app.config.DB_CONF['database'])
            ),
            create_db=True
        )
        db.generate_mapping(create_tables=True)
        app.db = db

    except Exception as e:
        msg = "An error ocurred building Infoenergia API: %s"
        logger.exception(msg, str(e))
        raise e
    else:
        logger.info("Build api finished")
        return app


app = build_app()


@app.listener('before_server_start')
async def server_init(app, loop):
    app.redis = await aioredis.create_redis_pool(app.config.REDIS_CONF)


@app.listener('after_server_stop')
def shutdown_app(app, loop):
    logger.info("Shuting down api... ")
    app.thread_pool.shutdown()
