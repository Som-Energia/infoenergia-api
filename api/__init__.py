import logging
import os
from concurrent import futures

from erppeek import Client
from sanic import Sanic
from sanic.log import logger
from sanic_jwt import Initialize, exceptions

from .contracts import bp_contracts
from .registration.login import authenticate, extra_views, InvitationUrlToken
from .registration.models import db

app = Sanic('infoenergia-api')


@app.listener('before_server_start')
def build_app(app, loop):
    from config import config
    try:
        app.config.from_object(config)

        Initialize(app, authenticate=authenticate, class_views=extra_views)
        app.blueprint(bp_contracts)

        auth_bp = app.blueprints['auth_bp']
        app.add_route(
            InvitationUrlToken.as_view(), '/auth/invitationtoken', host='localhost:9000'
        )

        app.thread_pool = futures.ThreadPoolExecutor(app.config.MAX_THREADS)
        app.erp_client = Client(**app.config.ERP_CONF)

        db.bind(
            provider='sqlite',
            filename=os.path.join(
                app.config.BASE_DIR,
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

@app.listener('after_server_stop')
def shutdown_app(app, loop):
    logger.info("Shuting down api... ")
    app.thread_pool.shutdown()
