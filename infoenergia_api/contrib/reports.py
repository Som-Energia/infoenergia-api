import aioredis
import aiohttp
import asyncio

import ssl
import json as jsonlib
from sanic.response import json
from sanic.log import logger

from ..utils import save_report

class beedataApi(object):

    def __init__(self):
        from infoenergia_api.app import app
        self._redis = app.redis
        self.N_WORKERS = app.config.N_WORKERS

        self.cert_file = app.config.CERT_FILE
        self.key_file = app.config.KEY_FILE
        self.company_id = app.config.COMPANY_ID
        self.base_url = app.config.BASE_URL
        self.apiversion = app.config.APIVERSION
        self.username = app.config.USERNAME
        self.password = app.config.PASSWORD

        self.login_url = "{}/authn/login".format(self.base_url)
        self.token = None

    async def login(self):
        login_credentials = {
            "username": self.username,
            "password": self.password
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.login_url, json=login_credentials, ssl=False) as response:
                content = await response.json()
                self.token = content['token']
                return response.status

    async def process_one_report(self, session, contractId):
        logger.info("start download of {}".format(contractId.decode()))
        status, report = await self.download_one_report(session, contractId.decode())

        if report is None:
            return False
        msg = "Download of {} with status {} for report {}"
        logger.info(msg.format(contractId, status, report['_meta']))
        logger.info("start save of {}".format(contractId))

        result = await save_report(report, contractId.decode())

        if not result:
            return False
        logger.info("done save of {} with result {}".format(contractId, result))
        return True

    async def worker(self, queue, session, results):
        while True:
            row = await queue.get()
            result = await self.process_one_report(session, row)
            results.append(result)
            if bool(result):
                await self._redis.lrem(b"key:reports", 0, row)

            # To do: Mark the item as processed, allowing queue.join() to keep
            # track of remaining work and know when everything is done.
            queue.task_done()

    async def process_reports(self, contractIdsList):
        await self.login()
        headers = {
          'X-CompanyId': str(self.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(self.token)
        }
        queue = asyncio.Queue(self.N_WORKERS)
        results = []
        async with aiohttp.ClientSession(headers=headers) as session:
            workers = [asyncio.create_task(self.worker(queue, session, results))
                       for _ in range(self.N_WORKERS)]
            for contractId in contractIdsList:
                await queue.put(contractId) # Feed the contractIds to the workers.
            await queue.join() # Wait for all enqueued items to be processed.

        for worker in workers:
            worker.cancel()

        unprocessed_reports = await self._redis.lrange(b"key:reports", 0, -1)
        msg = 'The following {} reports were NOT processed: {}'
        logger.warning(msg.format(len(unprocessed_reports), unprocessed_reports))

        return [report.decode() for report in unprocessed_reports]

    async def download_one_report(self, session, contractId):
        endpoint = "{}/{}/results_chart".format(self.base_url, self.apiversion)
        params = {'where': '"contractId"=="{}"'.format(contractId)}
        sslcontext = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile=self.cert_file
        )
        sslcontext.load_cert_chain(self.cert_file, self.key_file)
        async with session.get(endpoint, params=params, ssl=sslcontext) as response:
            report = await response.json()
            if response.status != 200 or report["_meta"]["total"] == 0:
                return response.status, None
            return response.status, report


async def get_report_ids(request):
    await request.app.redis.delete(b"key:reports")
    key, value = b"key:reports", "{}"

    ids = ["{}".format(id).encode() for id in request.json['contract_ids']]
    reports = await request.app.redis.rpush(
        key,
        *ids
    )
    logger.info("There are {} contractIds in redis to process".format(reports))
    return await request.app.redis.lrange(key, 0, -1)
