import asyncio
import pickle
from dataclasses import dataclass
from datetime import datetime

from sanic.log import logger

from config import config


async def get_report_ids(request):
    await request.app.ctx.redis.delete(b"key:reports")
    key, value = b"key:reports", "{}"

    ids = ["{}".format(id).encode() for id in request.json["contract_ids"]]
    reports = await request.app.ctx.redis.rpush(key, *ids)

    logger.info("There are {} contractIds in redis to process".format(reports))
    report_ids = await request.app.ctx.redis.lrange(key, 0, -1)
    return report_ids, request.json["month"], request.json["type"]


@dataclass
class ReportRequest:

    contract_ids: list
    month: str
    report_type: str
    date: str

    def as_dict(self):
        base_dict = self.__dict__
        base_dict["contract_ids"] = pickle.dumps(self.contract_ids)
        return base_dict

    async def save_report_request(self, redis_con, queue):
        result = await redis_con.hmset(queue, self._as_dict())
        return result


class BeedataReports(object):

    CCH_REPORTS_QUEUE = "tasks:cch_reports"
    CCH_REPORTS_DONE = "tasks:done:cch_reports"
    CCH_REPORTS_FAIL = "tasks:fail:cch_reports"

    def __init__(self, api_client, mongo_con, redis, **kwargs):
        self.api_client = api_client
        self.somenergia_db = mongo_con.somenergia
        self._redis = redis

        self.N_WORKERS = kwargs.get("n_workers", config.MAX_TASKS)

    async def process_reports(self, contract_ids, month, report_type):
        sem = asyncio.Semaphore(self.N_WORKERS)
        results = {}
        report_request = ReportRequest(
            contract_ids=contract_ids,
            month=month,
            report_type=report_type,
            date=str(datetime.now()),
        )

        await report_request.save_request(self._redis, self.CCH_REPORTS_QUEUE)

        tasks = [
            {
                asyncio.create_task(
                    self.process_one_report(month, report_type, contract_id, sem)
                ): contract_id
            }
            for contract_id in contract_ids
        ]

        to_do = tasks
        while to_do:
            done, to_do = asyncio.wait(to_do, timeout=config.TASKS_TIMEOUT)
            for task in done:
                try:
                    result = task.result()
                    results[result] = results.get(result, []).append(tasks[task])
                except Exception as e:
                    msg = (
                        "An unexpected error ocurred procesing task {} for "
                        "contract_id {}, reason: {}"
                    )
                    logger.error(msg.format(task, tasks[task], e))
                    results[False] = results.get(False, []).append(tasks[task])

        unprocessed_reports = results[False]
        msg = "The following {} reports were NOT processed: {}"
        logger.warning(msg.format(len(unprocessed_reports), unprocessed_reports))

        return [report.decode() for report in unprocessed_reports]

    async def process_one_report(self, month, report_type, contract_id, sem):
        with sem:
            logger.info("start download of {}".format(contract_id))
            _, report = await self.api_client.download_report(
                contract_id, month, report_type
            )
            if report is None:
                return bool(report)

            logger.info("start inserting doc for {}".format(contract_id))
            result = await self.save_report(report, report_type)
            return bool(result)

    async def save_report(self, reports, report_type):
        result = await self.somenergia_db[report_type].insert_many(
            [
                {
                    "contractName": item["contractId"],
                    "beedataUpdateDate": item["_updated"],
                    "beedataCreateDate": item["_created"],
                    "month": item["month"],
                    "type": item["type"],
                    "results": item["results"],
                }
                for item in reports
            ]
        )
        msg = "Inserted {} of the initial {} docs"
        logger.info(msg.format(len(result.inserted_ids), len(reports)))
        return result.inserted_ids
