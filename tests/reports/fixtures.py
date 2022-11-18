import json
import uuid
import pytest

from infoenergia_api.api.reports.models import (
    create_report_request,
    get_report_request,
)


@pytest.fixture
def uuid_id__one_contract():
    return uuid.UUID("12345678123456781234567812345678")


@pytest.fixture
def uuid_id__multiple_contracts():
    return uuid.UUID("87654321876543218765432187654321")


@pytest.fixture
def uuid_id__invalid_multiple_contracts():
    return uuid.UUID("78634521876541238765432187654321")


@pytest.fixture
def raw_report_request__one_contract():
    return json.dumps(
        {
            "id": "sep_2022",
            "contract_ids": ["0045900"],
            "type": "infoenergia_reports",
            "create_at": "2022-09-15",
            "month": "202209",
        }
    ).encode()


@pytest.fixture
def raw_report_request__multiple_contracts():
    return json.dumps(
        {
            "id": "sep_2022",
            "contract_ids": ["0045900", "0219358", "0064048"],
            "type": "infoenergia_reports",
            "create_at": "2022-09-15",
            "month": "202209",
        }
    ).encode()


@pytest.fixture
def raw_report_request__invalid_multiple_contracts():
    return json.dumps(
        {
            "id": "sep_2022",
            "contract_ids": ["0045900", "wertyu8", "0064048"],
            "type": "infoenergia_reports",
            "create_at": "2022-09-15",
            "month": "202209",
        }
    ).encode()


@pytest.fixture
async def report_request__one_contract(
    uuid_id__one_contract, raw_report_request__one_contract
):
    uuid_id = uuid_id__one_contract
    if (report_req := await get_report_request(id=uuid_id)) is None:
        report_req = await create_report_request(
            uuid_id, raw_report_request__one_contract
        )

    yield report_req


@pytest.fixture
async def report_request__multiple_contracts(
    uuid_id__multiple_contracts, raw_report_request__multiple_contracts
):
    uuid_id = uuid_id__multiple_contracts
    if (report_req := await get_report_request(id=uuid_id)) is None:
        report_req = await create_report_request(
            uuid_id, raw_report_request__multiple_contracts
        )

    yield report_req


@pytest.fixture
async def report_request__invalid_multiple_contracts(
    uuid_id__invalid_multiple_contracts, raw_report_request__invalid_multiple_contracts
):
    uuid_id = uuid_id__invalid_multiple_contracts
    if (report_req := await get_report_request(id=uuid_id)) is None:
        report_req = await create_report_request(
            uuid_id, raw_report_request__invalid_multiple_contracts
        )

    yield report_req
