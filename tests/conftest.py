import os
import pytest

from config import config
from infoenergia_api.api.utils import get_db_instance

from .fixtures import *
from .reports.fixtures import *


@pytest.fixture()
def db():
    _db = get_db_instance()
    try:
        _db.bind(
            provider="sqlite",
            filename=os.path.join(
                config.DATA_DIR, "{}.sqlite3".format(config.DB_CONF["database"])
            ),
            create_db=True,
        )
        _db.generate_mapping(create_tables=True)
    except:
        _db.create_tables()
    yield _db
    _db.drop_all_tables(with_all_data=True)
    _db.disconnect()


@pytest.fixture
async def mongo_conn(app):
    yield app.ctx.mongo_client


@pytest.fixture
async def beedata_reports__one_report(bapi, app, report_request__one_contract):
    beedata_rep = BeedataReports(
        bapi, app.ctx.mongo_client, report_request__one_contract
    )
    yield beedata_rep


@pytest.fixture
async def beedata_reports__multiple_reports(
    bapi, app, report_request__multiple_contracts
):
    beedata_rep = BeedataReports(
        bapi, app.ctx.mongo_client, report_request__multiple_contracts
    )
    yield beedata_rep
