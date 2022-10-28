from .exceptions import ApiError


def retry_expired(method):
    async def inner(*args, **kwargs):
        try:
            res = await method(*args, **kwargs)
        except ApiError as e:
            if e.status_code == 401:
                await args[0].reconnect()
                return await method(*args, **kwargs)
            raise e
        else:
            return res

    return inner
