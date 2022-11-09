import json
import uuid
import pytest


@pytest.fixture
def uuid_id():
    return uuid.UUID("12345678123456781234567812345678")


@pytest.fixture
def raw_report_request():
    return json.dumps(
        {
            "id": "summer_2020",
            "contract_ids": ["0180471", "0010012", "1000010"],
            "type": "CCH",
            "create_at": "2020-01-01",
            "month": "202011",
        }
    ).encode()
