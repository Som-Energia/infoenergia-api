import logging
import os
import ssl
from collections import namedtuple
from inspect import currentframe, getouterframes

import aiohttp

logger = logging.getLogger(__name__)


class ApiException(Exception):
    
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


class BeedataApiClient(object):
    '''
    Beedata Api Client for api described in:
    https://api.beedataanalytics.com/v1/docs
    '''
    ApiSession = namedtuple('ApiSession', 'token, headers, cookies')
    ApiResponse = namedtuple('ApiResponse', 'content, headers, cookies, status')
    _api_version = 'v1'

    _endpoints = {
        'login': 'authn/login',
        'logout': 'authn/logout',
        'download_report': f'{_api_version}/components',
    }

    _params = {
        'download_report': {
            'where': '',
        }
    }


    @classmethod
    async def create(
        cls, url, username, password, company_id, cert_file, cert_key, **kwargs
    ):
        self = cls()  
        self.base_url = url
        self.username = username
        self.__password = password
        self.cert_file = cert_file
        self.__cert_key = cert_key
        self.company_id = company_id
        self._headers = {
            'X-CompanyId': str(company_id)
        }
        self.api_sslcontext = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile=self.cert_file
        )
        self.api_sslcontext.load_cert_chain(self.cert_file, self.__cert_key)

        self.api_session = await self.login(username, password)
        return self

    async def _request(self, session, *args, **kwargs):
        frame = getouterframes(currentframe())[1]
        calling_function = frame[3]

        endpoint = self._endpoints[calling_function]

        url = os.path.join(
            self.base_url, endpoint
        )
        api_session = kwargs.get('api_session')
        headers = api_session and api_session.headers
        cookies = api_session and api_session.cookies
        url_params = self._get_url_params(calling_function, kwargs)
        if 'payload' in kwargs:
            async with session.post(
                url, json=kwargs['payload'], headers=headers, cookies=cookies, ssl=kwargs.get('ssl')
            ) as response:
                content = await response.json()
                if response.status < 400:
                    return self.ApiResponse(
                        content=content,
                        headers=response.headers,
                        cookies=response.cookies,
                        status=response.status
                    )
                raise ApiException(content.get('error', 'Unexpected request'), response.status) 
        async with session.get(
            url, params=url_params, headers=headers, cookies=cookies, ssl=kwargs.get('ssl')
        ) as response:
            content = await response.json()
            if response.status < 400:
                return self.ApiResponse(
                    content=content,
                    headers=response.headers,
                    cookies=response.cookies,
                    status=response.status
                )
            raise ApiException(content.get('error', 'Unexpected request'), response.status) 

    async def login(self, username=None, password=None):
        login_credentials = {
            "username": username or self.username,
            "password": password or self.__password
        }
        
        async with aiohttp.ClientSession() as session:
            response = await self._request(session, payload=login_credentials, ssl=False)
            return self.ApiSession(
                token=response.content['token'],
                cookies=response.cookies,
                headers=self._headers
            )

    async def logout(self):
        async with aiohttp.ClientSession() as session:
            return await self._request(session, api_session=self.api_session, ssl=self.api_sslcontext)

    def get_request_filter(self, contract_id, month, report_type):

        request_filter = {'contractId': f'\"{contract_id}\"'}

        if report_type == 'photovoltaic_reports':
            request_filter['type'] = 'FV'
        else:
            request_filter['month'] = month

        return [request_filter]

    async def download_report(self, contract_id, month, report_type):
        request_filter = self.get_request_filter(contract_id, month, report_type)
        
        async with aiohttp.ClientSession() as session:
            response = await self._request(
                session,
                where=request_filter,
                api_session=self.api_session,
                ssl=self.api_sslcontext
            )
            if response.content["_meta"]["total"] == 0:
                return response.status, None
            return response.status, response.content['_items']

    def _get_url_params(self, calling_function, kwargs):
        url_params = self._params.get(calling_function, {})
        if url_params and kwargs:
            for param in kwargs:
                if param in url_params:
                    url_params[param] = ''.join(
                        [' and '.join(
                            [f'\"{field}\"=={value}'
                            for field, value in condition.items()])
                        for condition in kwargs[param]
                        ]
                    )

            return url_params
        return {}
