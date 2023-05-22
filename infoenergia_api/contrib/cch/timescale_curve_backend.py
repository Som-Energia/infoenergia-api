from datetime import timedelta
from psycopg import AsyncClientCursor
from psycopg.rows import dict_row

from ...utils import (
    iso_format,
    iso_format_tz,
    increment_isodate,
    local_isodate_2_utc_isodatetime,
    naive_utc_datetime_2_utc_datetime,
)
from ..erpdb_manager import get_erpdb_instance


def cch_date_from_cch_utctimestamp(raw_data, measure_delta):
    utcdatetime = naive_utc_datetime_2_utc_datetime(
        naive_utc_datetime=raw_data['utc_timestamp'],
    )
    utcdatetime -= timedelta(**measure_delta)
    return iso_format_tz(utcdatetime)


class TimescaleCurveBackend:

    async def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        downloaded_from=None,
        downloaded_to=None,
        **extra_filter
    ):
        erpdb = await get_erpdb_instance()
        async with AsyncClientCursor(erpdb) as cursor:
            result = []
            if cups:
                result += [cursor.mogrify("name ILIKE %s", [cups[:20]+"%"])]
            if start:
                start_utc = local_isodate_2_utc_isodatetime(start)
                result += [cursor.mogrify("utc_timestamp >= %s",
                    [start_utc]
                )]
            if end:
                end_utc = local_isodate_2_utc_isodatetime(increment_isodate(end))
                result += [cursor.mogrify("utc_timestamp <= %s",
                    [end_utc]
                )]
            if downloaded_from:
                result += [cursor.mogrify("create_at >= %s", [downloaded_from+" 00:00:00"])]
            if downloaded_to:
                result += [cursor.mogrify("create_at <= %s", [downloaded_to+" 00:00:00"])]
            for key, value in extra_filter.items():
                result += [cursor.mogrify(f"{key} = %s", [value])]

        return result

    async def get_curve(
        self,
        curve_type,
        start, end,
        downloaded_from=None, downloaded_to=None,
        cups=None
    ):
        def cch_transform(cch):
            return dict(
                cch,
                date=cch_date_from_cch_utctimestamp(cch, curve_type.measure_delta),
                dateDownload=iso_format(cch["create_at"]),
                dateUpdate=iso_format(cch["update_at"]),
                datetime=iso_format(cch["datetime"]),
                utc_timestamp=iso_format(cch["utc_timestamp"]),
            )

        query = await self.build_query(
            start=start, end=end,
            downloaded_from=downloaded_from, downloaded_to=downloaded_to,
            cups=cups,
            **curve_type.extra_filter
        )
        erpdb = await get_erpdb_instance()
        async with AsyncClientCursor(erpdb, row_factory=dict_row) as cursor:
            await cursor.execute(f"""
                SELECT * from {curve_type.model}
                WHERE {" AND ".join(query) or "TRUE"}
                ORDER BY utc_timestamp
                ;
            """)
            return [
                cch_transform(cch) for cch in await cursor.fetchall()
            ]
