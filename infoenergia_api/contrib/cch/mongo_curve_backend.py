from datetime import timedelta
from ..mongo_manager import get_mongo_instance
from ...utils import (
    iso_format,
    iso_format_tz,
    increment_isodate,
    local_isodate_2_naive_local_datetime,
    naive_local_isodatetime_2_utc_datetime,
)

def cch_date_from_cch_datetime(cch, measure_delta):
    utcdatetime = naive_local_isodatetime_2_utc_datetime(
        naive_local_isodate = cch['datetime'],
        is_dst = cch['season'],
    )
    utcdatetime -= timedelta(**measure_delta)
    return iso_format_tz(utcdatetime)

class MongoCurveBackend():

    def __init__(self):
        mongo_client = get_mongo_instance()
        self.db = mongo_client.somenergia

    def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        downloaded_from=None,
        downloaded_to=None,
        **extra_filter
    ):
        query = {}
        if start:
            query.setdefault('datetime', {}).update(
                {"$gte": local_isodate_2_naive_local_datetime(start)}
            )
        if end:
            query.setdefault('datetime', {}).update(
                {"$lte": local_isodate_2_naive_local_datetime(increment_isodate(end))}
            )
        if downloaded_from:
            query.setdefault('create_at', {}).update(
                {"$gte": local_isodate_2_naive_local_datetime(downloaded_from)}
            )
        if downloaded_to:
            query.setdefault('create_at', {}).update(
                {"$lte": local_isodate_2_naive_local_datetime(downloaded_to)}
            )
        for key, value in extra_filter.items():
            query.update({key: {"$eq": value}})
        if cups:
            query.update(name={"$regex": "^{}".format(cups[:20])})
        return query

    async def get_curve(self, curve_type, start, end, cups=None):
        query = self.build_query(start, end, cups, **curve_type.extra_filter)
        cch_collection = self.db[curve_type.model]

        def cch_transform(cch):
            return dict(cch,
                id=int(cch['id']), # un-bson-ize
                date=cch_date_from_cch_datetime(cch, curve_type.measure_delta),
                dateDownload=iso_format(cch["create_at"]),
                dateUpdate=iso_format(cch["update_at"]),
            )

        result = [
            cch_transform(cch)
            async for cch in cch_collection.find(
                filter=query,
                # exclude _id since it is not serializable
                projection=dict(_id=False),
                #sort=[( "datetime", 1 )],
            )
        ]
        return result


