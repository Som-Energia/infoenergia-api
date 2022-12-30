import os

import pytest

from config import config
from infoenergia_api.api.utils import get_db_instance
from infoenergia_api.contrib.reports import BeedataReports

from .fixtures import *
from .reports.fixtures import *
from .erp.tariff.fixtures import _20TD_tariff_id


@pytest.fixture
def db():
    """
    Returns db instance
    """
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
        pass
    yield _db


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


@pytest.fixture
async def beedata_reports__invalid_multiple_reports(
    bapi, app, report_request__invalid_multiple_contracts
):
    beedata_rep = BeedataReports(
        bapi, app.ctx.mongo_client, report_request__invalid_multiple_contracts
    )
    yield beedata_rep
