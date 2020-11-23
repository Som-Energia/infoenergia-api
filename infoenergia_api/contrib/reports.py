import asyncio
import aioredis
import aiohttp
import ssl
import json as jsonlib
from sanic.response import json


async def process_report(request):
    process_reports = await request.app.redis.set(
        'reports',
        jsonlib.dumps(request.json['contract_ids'])
    )

    return  jsonlib.loads(await request.app.redis.get('reports'))


async def login(login_url, username=None, password=None):
    login_credentials = {
        "username": username,
        "password": password
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=login_credentials, ssl=False) as response:
            content = await response.json()
            return response.status, content


async def download_reports(base_url, apiversion, company_id, token, contractId):
    endpoint = base_url + "/" + apiversion + "/results_chart"
    params = {'where': f'"contractId"=="{contractId}"'}
    headers = {
      'X-CompanyId': str(company_id),
      'Cookie': f'iPlanetDirectoryPro={token}'
    }

    sslcontext = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile='/home/joana/Downloads/cert.crt')
    sslcontext.load_cert_chain('/home/joana/Downloads/cert.crt', '/home/joana/Downloads/cert.key')
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(endpoint, params=params, ssl=sslcontext) as response:
            content = await response.json()
            return response.status, content
