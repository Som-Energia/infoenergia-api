import asyncio

from sanic.log import logger


async def get_report_ids(request):
    await request.app.redis.delete(b"key:reports")
    key, value = b"key:reports", "{}"

    ids = ["{}".format(id).encode() for id in request.json['contract_ids']]
    reports = await request.app.redis.rpush(
        key,
        *ids
    )
    logger.info("There are {} contractIds in redis to process".format(reports))
    report_ids = await request.app.redis.lrange(key, 0, -1)
    return report_ids, request.json['month'], request.json['type']


class Beedata(object):

    def __init__(self, api_client, mongo_con, redis, **kwargs):
        self.api_client = api_client
        self.somenergia_db = mongo_con.somenergia
        self._redis = redis

        self.N_WORKERS = kwargs.get('n_workers', 10)

    async def process_one_report(self, month, report_type, contract_id):
        logger.info("start download of {}".format(contract_id.decode()))
        status, report = await self.api_client.download_report(contract_id.decode(), month, report_type)
        if report is None:
            return bool(report)

        logger.info("start inserting doc for {}".format(contract_id))
        result = await self.save_report(report)
        return bool(result)

    async def worker(self, queue, month, report_type, results):
        while True:
            contract_id = await queue.get()
            result = await self.process_one_report(month, report_type, contract_id)
            results.append(result)
            if result:
                await self._redis.lrem(b"key:reports", 0, contract_id)
            # To do: Mark the item as processed, allowing queue.join() to keep
            # track of remaining work and know when everything is done.
            queue.task_done()

    async def process_reports(self, contractIdsList, month, report_type):
        queue = asyncio.Queue(self.N_WORKERS)
        results = []
        workers = [asyncio.create_task(self.worker(queue, month, report_type, results)) for _ in range(self.N_WORKERS)]
        for contractId in contractIdsList:
            await queue.put(contractId) # Feed the contractIds to the workers.
        await queue.join() # Wait for all enqueued items to be processed.

        for worker in workers:
            worker.cancel()

        unprocessed_reports = await self._redis.lrange(b"key:reports", 0, -1)
        msg = 'The following {} reports were NOT processed: {}'
        logger.warning(msg.format(len(unprocessed_reports), unprocessed_reports))
        await self.api_client.logout()

        return [report.decode() for report in unprocessed_reports]

    async def save_report(self, reports):
        result = await self.somenergia_db.infoenergia_reports.insert_many([
            {
                'contractName': item['contractId'],
                'beedataUpdateDate': item['_updated'],
                'beedataCreateDate': item['_created'],
                'month': item['month'],
                'results': item['results'],
            }  for item in reports
        ])
        msg = "Inserted {} of the initial {} docs"
        logger.info(msg.format(len(result.inserted_ids), len(reports)))
        return result.inserted_ids