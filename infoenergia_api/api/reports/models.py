import enum
import hashlib
import json
import uuid
from datetime import datetime

from pony.orm import Json, PrimaryKey, Required, db_session

from ..utils import get_db_instance

db = get_db_instance()


class ReportStates(enum.Enum):
    RECEIVED = "received"

    PROCESSING = "processing"

    DONE = "done"

    FAIL = "fail"


class ReportRequest(db.Entity):
    _table_ = "report_request"

    id = PrimaryKey(uuid.UUID, auto=False)

    md5 = Required(str, index=True)

    request_body = Required(Json)

    state = Required(str, default=ReportStates.RECEIVED.value)

    date = Required(datetime, default=datetime.now, index=True)

    def __repr__(self) -> str:
        return f"<ReportRequest:{self.md5}, state={self.state}>"


async def create_report_request(id_, raw_report_request):
    md5 = hashlib.md5(raw_report_request).hexdigest()
    request_body = json.loads(raw_report_request)

    with db_session:
        report_request = ReportRequest(
            id=id_,
            md5=md5,
            request_body=request_body,
        )

    return report_request
