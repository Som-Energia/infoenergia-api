import os
import pytest

from config import config
from infoenergia_api.api.utils import get_db_instance

from .fixtures import (
    app,
    async_client,
    auth_token,
    bapi,
    beedata,
    client,
    f1_id,
    f5d_id,
    mock_process_reports,
    mocked_next_cursor,
    p1_id,
    p2_id,
    scenarios,
    user,
    beedata_api_bad_credentials,
    beedata_api_correct_credentials,
)

from .reports.fixtures import *


@pytest.fixture(scope="session")
def db():
    _db = get_db_instance()
    _db.bind(
        provider="sqlite",
        filename=os.path.join(
            config.DATA_DIR, "{}.sqlite3".format(config.DB_CONF["database"])
        ),
        create_db=True,
    )
    _db.generate_mapping(create_tables=True)
    yield _db
    _db.disconnect()
    _db.drop_all_tables(with_all_data=True)
