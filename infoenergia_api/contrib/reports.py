import aioredis
import aiohttp
import asyncio

import ssl
import json as jsonlib
from sanic.response import json
from sanic.log import logger


class beedataApi(object):

    def __init__(self):
        from infoenergia_api.app import app

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
        print("start download of {}".format(contractId))
        status, report = await self.download_one_report(session, contractId)

        print("finished download of {} with status {} for report {}".format(contractId, status, report))

        if report is None:
            msg = "Download of {} with status {} for report {}"
            logger.warning(msg.format(contractId, status, report))
            return False

        print("start save of {}".format(contractId))

        # TODO returns last id
        result = await save_report(report)

        print("done save of {} with result {}".format(contractId, result))

        if not result:
            return False

        return True

    async def worker(self, queue, session, results):
        while True:
            row = await queue.get()
            result = await self.process_one_report(session, row)
            results.append(result)
            #if result == True:
            #   remove from redis
            # else
            #  error, don't remove from redis, just mark as done

            # Mark the item as processed, allowing queue.join() to keep
            # track of remaining work and know when everything is done.
            queue.task_done()

    async def process_reports(self, contractIdsList):
        headers = {
          'X-CompanyId': str(self.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(self.token)
        }

        rows = contractIdsList

        N_WORKERS = 2
        queue = asyncio.Queue(N_WORKERS)
        results = []
        async with aiohttp.ClientSession(headers=headers) as session:
            workers = [asyncio.create_task(self.worker(queue, session, results))
                       for _ in range(N_WORKERS)]
            # Feed the contractIds to the workers.
            for row in rows:
                await queue.put(row)
            # Wait for all enqueued items to be processed.
            await queue.join()

        for worker in workers:
            worker.cancel()

        if not all(results):
            return False
        return True

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
    print(*request.json['contract_ids'])

    key, value = b"key:lset", "value:{}"
    values = [value.format(i).encode("utf-8") for i in range(0, 3)]
    key = b"key:reports"

    ids = ["value:{}".format(id).encode('utf-8') for id in request.json['contract_ids']]
    reports = await request.app.redis.rpush(
        key,
        *ids
    )

    contractIds = await request.app.redis.get('reports')
    contractId = contractIds[0]
    print("contract id from redis reports {}".format(contractId))

    result = await request.app.redis.lrem(key, 1, "value:{}".format(contractId).encode("utf-8"))
    print(result)
    return jsonlib.loads(contractId)


async def save_report(report):
    from infoenergia_api.app import app
    infoenergia_reports = app.mongo_client.somenergia.infoenergia_reports
    result = await infoenergia_reports.insert_one(report)
    return result.inserted_id


async def read_report(reportId):
    from infoenergia_api.app import app
    infoenergia_reports = app.mongo_client.somenergia.infoenergia_reports
    report = await infoenergia_reports.find_one(reportId)
    return report
