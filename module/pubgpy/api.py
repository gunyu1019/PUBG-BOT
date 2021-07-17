"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import aiohttp
import json
import logging

from . import errors
from .enums import Platforms

log = logging.getLogger(__name__)


class Api:
    """ Used to report with the PUBG API.

    Parameters
    ----------
    token : str
        Contains the token value issued by the PUBG API.
        If you have not been issued or if you forget, please get the key from https://developer.pubg.com/.
    platform : `str` or `Platforms`, optional
         `Platforms` information to report with API by substituting the value of `Platform` or string.
        Sometimes the platform type is not required for some features that do not require it.
    """
    def __init__(self, token: str, platform: (str, Platforms) = None):
        self.token = token

        self.BASE_URL = "https://api.pubg.com"
        if isinstance(platform, Platforms):
            self.platform = platform.value
        else:
            self.platform = platform

    async def requests(self, method: str, path: str, ni_shards: bool = True, **kwargs):
        """
        Function that interacts with api.
        This function attempts to interact with the API.

        Parameters
        ----------
        method : str
            HTTP Request Method
        path : str
             Endpoint of the PUBG API. BASE address for "https://api.pubg.com" is included.
        ni_shards : bool, default: True
            Select whether to include platform information. Some endpoints, such as tournaments and samples,
             do not distinguish platform information. Therefore, you need to set this value to False to use some
            functions. Default is True.
        **kwargs :
            Used to add content to header you request.

        Returns
        -------
        dict
            Returns the value report with the PUBG API.

        Raises
        ------
        errors.Unauthorized
            Token value is required or missing. Alternatively, it also occurs if the token value does not match.
        errors.NotFound
            Couldn't find the value you required.
        errors.UnsupportedMediaType
            Unsupported media type.
        errors.TooManyRequests
            When requested too much, it is returned. By default, PUBG API can request up to 10 times per minute.
        """
        header = {
            "accept": "application/vnd.api+json",
            "Authorization": "Bearer {}".format(self.token)
        }
        header.update(**kwargs)

        if ni_shards:
            url = "{}/shards/{}{}" .format(self.BASE_URL, self.platform, path)
        else:
            url = "{}{}" .format(self.BASE_URL, path)
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=header) as resp:
                log.debug("A request has been received. '{}'".format(url))
                if resp.content_type == "application/json":
                    data = await resp.json()
                else:
                    fp_data = await resp.text()
                    data = json.loads(fp_data)

                if resp.status == 200:
                    log.debug("Successfully received API results.")
                    return data
                elif resp.status == 401:
                    log.error("Failed to get response: Unauthorized (Status Code: {})".format(resp.status))
                    raise errors.Unauthorized(resp, data)
                elif resp.status == 404:
                    log.error("Failed to get response: Not Found (Status Code: {})".format(resp.status))
                    raise errors.NotFound(resp, data)
                elif resp.status == 415:
                    log.error("Failed to get response: Unsupported Media Type (Status Code: {})".format(resp.status))
                    raise errors.UnsupportedMediaType(resp, data)
                elif resp.status == 429:
                    log.error("Failed to get response: Too Many Requests (Status Code: {})".format(resp.status))
                    raise errors.TooManyRequests(resp, data)
                else:
                    log.error("Failed to get response: {} (Status Code: {})".format(resp.reason, resp.status))
                    raise errors.APIException(resp, data)

    async def get(self, path, ni_shards: bool = True, **kwargs):
        """
        Same as :function:`requests`. Only, method is called GET.

        Parameters
        ----------
        path : str
             Endpoint of the PUBG API. BASE address for "https://api.pubg.com" is included.
        ni_shards : bool, default: True
            Select whether to include platform information. Some endpoints, such as tournaments and samples,
             do not distinguish platform information. Therefore, you need to set this value to False to use some
            functions. Default is True.
        **kwargs :
            Used to add content to header you request.

        Returns
        -------
        dict
            Returns the value report with the PUBG API.

        Raises
        ------
        errors.Unauthorized
            Token value is required or missing. Alternatively, it also occurs if the token value does not match.
        errors.NotFound
            Couldn't find the value you required.
        errors.UnsupportedMediaType
            Unsupported media type.
        errors.TooManyRequests
            When requested too much, it is returned. By default, PUBG API can request up to 10 times per minute.
        """
        return await self.requests(method="GET", path=path, ni_shards=ni_shards, **kwargs)
