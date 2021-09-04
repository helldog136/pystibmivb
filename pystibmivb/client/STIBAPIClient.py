"""Common attributes and functions."""
import asyncio
import base64
import logging
import time
from abc import ABC, abstractmethod

import aiohttp
import async_timeout
from yarl import URL

LOGGER = logging.getLogger(__name__)

API_BASE_URL = 'https://opendata-api.stib-mivb.be'
PASSING_TIME_BY_POINT_SUFFIX = "/OperationMonitoring/4.0/PassingTimeByPoint/"


class OAuthTokenManager(object):
    def __init__(
            self,
            session,
            client_id,
            client_secret,
            url,
            *,
            renew_pad_secs=60,
            **parameters
    ):
        self.session = session
        self.client_secret = client_secret
        self.client_id = client_id
        self.url = url
        self.parameters = parameters
        self.renew_pad_secs = renew_pad_secs

        self._token = None
        self._exp = None

    async def login(self):
        headers = {}
        headers[
            'Authorization'] = f'Basic {str(base64.b64encode((self.client_id + ":" + self.client_secret).encode("utf-8")), "utf-8")}'
        try:
            async with async_timeout.timeout(5):
                response = await self.session.post(data={"grant_type": "client_credentials"},
                                                   url=self.url,
                                                   headers=headers)
                body = {}
                if response.content_type == "application/json":
                    body = await response.json()
                else:
                    raise aiohttp.ClientError("Unexpected content type: got " + response.content_type)
                self._token = body['access_token']
                self._exp = time.time() + body['expires_in'] - self.renew_pad_secs
        except aiohttp.ClientError as error:
            LOGGER.error("Error fetching token for STIB/MIVB : %s", error)
        except asyncio.TimeoutError as error:
            LOGGER.debug("Timeout connecting to STIB/MIVB API: %s", error)

    def is_token_valid(self):
        return self._token and self._exp and time.time() < self._exp

    @property
    def token(self):
        return self._token


class AbstractSTIBAPIClient(ABC):
    @abstractmethod
    async def api_call(self, endpoint_suffix: str, additional_headers=None):
        pass

    @abstractmethod
    async def api_call_passingTimeByPoint_for_stop_id(self, point_id: str) -> dict:
        pass

    @abstractmethod
    async def api_call_passingTimeByPoint_for_stop_ids(self, point_ids: list) -> dict:
        pass


class STIBAPIAuthClient:
    def __init__(self, session: aiohttp.ClientSession, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_manager = OAuthTokenManager(session,
                                               self.client_id, self.client_secret,
                                               API_BASE_URL + '/token', )

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        if self.token_manager.is_token_valid():
            return self.token_manager.token

        await self.token_manager.login()

        return self.token_manager.token


class STIBAPIClient(AbstractSTIBAPIClient):
    """A class for common functions."""

    def __init__(self,
                 loop: asyncio.events.AbstractEventLoop,
                 session: aiohttp.ClientSession,
                 authClient: STIBAPIAuthClient):
        """Initialize the class."""
        self.authClient = authClient
        self.loop = loop
        self.session = session

    async def api_call_passingTimeByPoint_for_stop_id(self, point_id: str) -> dict:
        return await self.api_call(PASSING_TIME_BY_POINT_SUFFIX + point_id)

    async def _api_call_passingTimeByPoint_for_10_stop_ids(self, point_ids: list) -> dict:
        return await self.api_call(PASSING_TIME_BY_POINT_SUFFIX + "%2C".join(point_ids))

    async def api_call_passingTimeByPoint_for_stop_ids(self, point_ids: set) -> dict:
        res = {"points": []}
        subset_point_ids = []
        for i in range(1, len(point_ids) + 1):
            subset_point_ids.append(point_ids.pop())
            if i % 10 == 0 or len(point_ids) == 0:
                subset_res = await self._api_call_passingTimeByPoint_for_10_stop_ids(subset_point_ids)
                res["points"].extend(subset_res["points"])
                subset_point_ids = []
        return res

    async def api_call(self, endpoint_suffix: str, additional_headers=None):
        if additional_headers is None:
            additional_headers = {}

        """Call the API."""
        headers = {'Authorization': "Bearer " + await self.authClient.async_get_access_token()}
        headers.update(additional_headers)
        data = None
        try:
            async with async_timeout.timeout(30, loop=self.loop):
                called_url = URL(API_BASE_URL + endpoint_suffix, encoded=True)
                LOGGER.debug("Endpoint URL: %s", str(called_url))
                response = await self.session.get(url=called_url, headers=headers)
                if response.content_type.upper() == "APPLICATION/JSON":
                    data = await response.json()
                elif response.content_type.upper() == "APPLICATION/ZIP":
                    if response.headers.get('Transfer-Encoding') == 'chunked':
                        buffer = b""
                        async for dt, end_of_http_chunk in response.content.iter_chunks():
                            buffer += dt
                            if end_of_http_chunk:
                                data = buffer
                    else:
                        data = await response.read()
                else:
                    data = await response.read()
        except aiohttp.ClientError as error:
            LOGGER.error("Error connecting to STIB/MIVB API: %s", error)
        except asyncio.TimeoutError as error:
            LOGGER.debug("Timeout connecting to STIB/MIVB API: %s", error)
        return data

    async def close(self):
        """Close the session."""
        await self.session.close()
