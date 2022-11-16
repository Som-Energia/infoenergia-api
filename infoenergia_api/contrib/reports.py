import asyncio
from datetime import datetime
from pymongo.errors import WriteError
from sanic.log import logger

from config import config


class BeedataReports(object):
    def __init__(self, api_client, mongo_con, report_request):
        self.api_client = api_client
        self.somenergia_db = mongo_con.somenergia
        self.report_request = report_request

    @property
    def reports(self):
        return self.report_request.request_body["contract_ids"]

    async def process_reports(self):
        sem = asyncio.Semaphore(config.MAX_THREADS)
        results = dict()

        tasks = {
            asyncio.create_task(
                self.process_one_report(
                    self.report_request.month,
                    self.report_request.report_type,
                    contract_id,
                    sem,
                )
            ): contract_id
            for contract_id in self.report_request.request_body["contract_ids"]
        }
        to_do = tasks
        while to_do:
            done, to_do = await asyncio.wait(to_do, timeout=config.TASKS_TIMEOUT)
            for task in done:
                try:
                    result = task.result()
                    results[result] = results.get(result, []) + [(tasks[task])]
                except Exception as e:
                    msg = (
                        "An unexpected error ocurred procesing task {} for "
                        "contract_id {}, reason: {}"
                    )
                    logger.error(msg.format(task, tasks[task], e))
                    results[False] = results.get(False, []) + [tasks[task]]
        processed_reports = results.get(True, [])
        unprocessed_reports = results.get(False, [])
        if unprocessed_reports:
            msg = "The following {} reports were NOT processed: {}"
            logger.warning(msg.format(len(unprocessed_reports), unprocessed_reports))

        return unprocessed_reports, processed_reports

    async def process_one_report(self, month, report_type, contract_id, sem):
        async with sem:
            msg = f"Download report ({report_type} - {month}) for <{contract_id}>"
            logger.info(msg)
            _, report = await self.api_client.download_report(
                contract_id, month, report_type
            )
            if report is None:
                return bool(report)

            result = await self.save_report(report, report_type)
            return bool(result)

    async def save_report(self, report, report_type):
        result = await self.somenergia_db[report_type].find_one_and_replace(
            {
                "contractName": report["contractId"],
                "month": report["month"],
                "type": report["type"],
            },
            {
                "contractName": report["contractId"],
                "beedataUpdateDate": report["_updated"],
                "beedataCreateDate": report["_created"],
                "month": report["month"],
                "type": report["type"],
                "results": report["results"],
                "meta": {
                    "_inserted_date": datetime.now(),
                    "_id": report["_id"],
                    "_etag": report["_etag"],
                },
            },
            upsert=True,
        )
        msg = "Inserted report (%s - %s) for <%s>"
        logger.info(msg, report["type"], report["month"], report["contractId"])
        return result
