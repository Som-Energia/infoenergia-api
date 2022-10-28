import asyncio
import os
import ssl
from collections import namedtuple
from inspect import currentframe, getouterframes

import aiohttp

from .exceptions import ApiError, NotUrlFoundError
from .utils import retry_expired


ApiSession = namedtuple("ApiSession", "token, headers, cookies")
ApiResponse = namedtuple("ApiResponse", "content, headers, cookies, status")


class BeedataApiClient(object):
    """
    Beedata Api Client for api described in:
    https://api.beedataanalytics.com/v1/docs
    """

    REPORT_TYPES = {"photovoltaic_reports": "FV", "infoenergia_reports": "CCH"}
    COMPANY_HEADER = "X-CompanyId"

    _api_version = "v1"

    _endpoints = {
        "login": "authn/login",
        "logout": "authn/logout",
        "download_report": f"{_api_version}/components",
        "reconnect": f"{_api_version}/",
    }

    _params = {
        "download_report": {
            "where": "",
        }
    }

    @classmethod
    async def create(cls, url, username, password, company_id, cert_file, cert_key):
        self = cls()
        self.base_url = url

        self.username = username
        self.__password = password

        self.cert_file = cert_file
        self.__cert_key = cert_key

        self.company_id = company_id
        self._headers = {self.COMPANY_HEADER: str(company_id)}

        self.api_sslcontext = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH, cafile=self.cert_file
        )
        self.api_sslcontext.load_cert_chain(self.cert_file, self.__cert_key)

        self.http_session = aiohttp.ClientSession()
        self.api_session = await self.login(username, password)

        return self

    async def login(self, username=None, password=None):
        login_credentials = {
            "username": username or self.username,
            "password": password or self.__password,
        }

        response = await self._request(payload=login_credentials, ssl=False)

        return ApiSession(
            token=response.content["token"],
            cookies=response.cookies,
            headers=self._headers,
        )

    async def logout(self):
        return await self._request(
            api_session=self.api_session, ssl=self.api_sslcontext
        )

    async def reconnect(self):
        self.api_session = await self.login()

    @retry_expired
    async def download_report(self, contract_id, month, report_type):
        filters = self._get_filters(contract_id, month, report_type)

        response = await self._request(
            where=filters,
            api_session=self.api_session,
            ssl=self.api_sslcontext,
        )
        if response.content["_meta"]["total"] == 0:
            return response.status, None
        return response.status, response.content["_items"][0]

    def _get_filters(self, contract_id, month, report_type):
        filters = {
            "contractId": f'"{contract_id}"',
            "month": month,
        }
        if type_ := self.REPORT_TYPES.get(report_type, ""):
            filters["type"] = type_

        if report_type == "photovoltaic_reports":
            del filters["month"]

        return [filters]

    async def _request(self, **kwargs) -> ApiResponse:
        """
        Clojure that make a request to beedata api endpoints
        """

        api_session = kwargs.get("api_session")
        headers = api_session and api_session.headers
        cookies = api_session and api_session.cookies

        async def _do_get(url, url_params, headers, cookies, ssl):
            async with self.http_session.get(
                url,
                params=url_params,
                headers=headers,
                cookies=cookies,
                ssl=ssl,
            ) as response:
                content = await response.json()
                if response.status >= 400:
                    raise ApiError(
                        content.get("error", "Unexpected request"), response.status
                    )
                return ApiResponse(
                    content=content,
                    headers=response.headers,
                    cookies=response.cookies,
                    status=response.status,
                )

        async def _do_post(url, payload, headers, cookies, ssl):
            async with self.http_session.post(
                url,
                json=payload,
                headers=headers,
                cookies=cookies,
                ssl=ssl,
            ) as response:
                content = await response.json()
                if response.status >= 400:
                    raise ApiError(
                        content.get("error", "Unexpected request"), response.status
                    )
                return ApiResponse(
                    content=content,
                    headers=response.headers,
                    cookies=response.cookies,
                    status=response.status,
                )

        url = self._get_url()

        if "payload" in kwargs:
            return await _do_post(
                url, kwargs["payload"], headers, cookies, kwargs.get("ssl")
            )

        url_params = self._get_query_params(**kwargs)
        return await _do_get(url, url_params, headers, cookies, kwargs.get("ssl"))

    def _get_url(self):
        frames = getouterframes(currentframe())
        calling_function = frames[2].function
        endpoint = self._endpoints.get(calling_function)

        if not endpoint:
            raise NotUrlFoundError(endpoint)

        url = os.path.join(self.base_url, endpoint)
        return url

    def _get_query_params(self, **kwargs):
        frames = getouterframes(currentframe())
        calling_function = frames[2].function
        url_params = self._params.get(calling_function, {})

        if url_params and kwargs:
            for param in kwargs:
                if param in url_params:
                    url_params[param] = "".join(
                        [
                            " and ".join(
                                [
                                    f'"{field}"=={value}'
                                    for field, value in condition.items()
                                ]
                            )
                            for condition in kwargs[param]
                        ]
                    )
        return url_params

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.logout())
            loop.run_until_complete(self.http_session.close())
        finally:
            pass
