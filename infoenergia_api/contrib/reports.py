import asyncio
import aioredis
import json as jsonlib


async def process_report(request):
    process_reports = await request.app.redis.set(
        'reports',
        jsonlib.dumps(request.json['contract_ids'])
    )
    return request.app.redis.mget('reports')
