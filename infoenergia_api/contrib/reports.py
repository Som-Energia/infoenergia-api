import asyncio
import aioredis
import aiohttp
import json as jsonlib


async def process_report(request):
    process_reports = await request.app.redis.set(
        'reports',
        jsonlib.dumps(request.json['contract_ids'])
    )

    return  jsonlib.loads(await request.app.redis.get('reports'))


async def login(base_url, username=None, password=None):
    login_url = base_url + "/authn/login"
    login_credentials = {
        "username": username,
        "password": password
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=login_credentials, ssl=False) as response:
            return response



