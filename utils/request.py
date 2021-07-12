import aiohttp

from utils.model import RequestsModel
from utils.exception import NotFound, ServiceUnavailable, InternalServerError, BadRequest, TooManyRequests, Forbidden, UnsupportedMediaType
from utils.token import PUBG_API

platform_site = ["steam", "kakao", "xbox", "psn", "stadia"]
DB_platform = ["Steam", "Kakao", "XBOX", "PSN", "Stadia"]


async def check_content(resp):
    if resp.content_type.startswith("application/json"):
        return await resp.json()
    elif resp.content_type.startswith("image/"):
        return await resp.content.read()
    elif resp.content_type.startswith("text/html"):
        return await resp.text()
    else:
        return None


async def requests(method: str, url: str, raise_on: bool = False):
    header = {
        "Authorization": "Bearer " + PUBG_API,
        "Accept": "application/vnd.api+json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, header=header) as resp:
            data = await check_content(resp)
            request_data = {
                "status": resp.status,
                "data": data,
                "version": resp.version,
                "content-type": resp.content_type,
                "reason": resp.reason
            }

            if raise_on:
                if request_data.get("status") == 400:
                    raise BadRequest(resp)
                elif request_data.get("status") == 403:
                    raise Forbidden(resp)
                elif request_data.get("status") == 404:
                    raise NotFound(resp)
                elif request_data.get("status") == 415:
                    raise UnsupportedMediaType(resp)
                elif request_data.get("status") == 429:
                    raise TooManyRequests(resp)
                elif request_data.get("status") == 500:
                    raise InternalServerError(resp)
                elif request_data.get("status") == 503:
                    raise ServiceUnavailable(resp)
            return RequestsModel(request_data)
