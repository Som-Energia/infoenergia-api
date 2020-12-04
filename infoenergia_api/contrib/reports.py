import asyncio
import aioredis
import aiohttp
import ssl
import json as jsonlib
from sanic.response import json


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

    async def download_reports(self, contractId):
        endpoint = "{}/{}/results_chart".format(self.base_url, self.apiversion)
        params = {'where': '"contractId"=="{}"'.format(contractId)}
        headers = {
          'X-CompanyId': str(self.company_id),
          'Cookie': 'iPlanetDirectoryPro={}'.format(self.token)
        }

        sslcontext = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile=self.cert_file
        )
        sslcontext.load_cert_chain(self.cert_file, self.key_file)
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(endpoint, params=params, ssl=sslcontext) as response:
                report = await response.json()
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
