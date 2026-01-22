"""
MIT License

Copyright (c) 2021-present MrArkon

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

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any, Optional

import aiohttp

from .errors import BadRequest, Forbidden, HTTPException, NotFound, Unauthorized
from .models import Anime, Genre

__all__ = ("Client",)
__log__: logging.Logger = logging.getLogger(__name__)

BASE: str = "https://kitsu.io/api/edge"
AUTH_BASE: str = "https://kitsu.io/api/oauth"


class Client:
    """User client used to interact with the Kitsu API"""

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> None:
        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()
        self._CLIENT_ID: Optional[str] = client_id
        self._CLIENT_SECRET: Optional[str] = client_secret

        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    def __repr__(self) -> str:
        return "<kitsu.Client>"

    def __add_client_info(self, data: dict) -> dict:
        if self._CLIENT_ID and self._CLIENT_SECRET:
            data["client_id"] = self._CLIENT_ID
            data["client_secret"] = self._CLIENT_SECRET
        return data

    async def _post(self, url: str, **kwargs: Any) -> Any:
        """Performs a POST request to the Kitsu API"""

        headers = kwargs.get("headers", {})
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = "Kitsu.py (https://github.com/SageTendo/kitsu.py)"

        data = kwargs.get("data", {})

        __log__.debug("Request URL: %s", url)
        __log__.debug("Request Headers: %s", headers)
        __log__.debug("Request Body: %s", data)

        async with self._session.post(url=url, headers=headers, json=data) as response:
            data = await response.json()

            if response.status == 200:
                return data
            if response.status == 400:
                raise BadRequest(response, data["error_description"])
            if response.status == 404:
                raise NotFound(response, data["error_description"])

            raise HTTPException(response, await response.text(), response.status)

    async def _get(self, url: str, **kwargs: Any) -> Any:
        """Performs a GET request to the Kitsu API"""

        headers = kwargs.pop("headers", {})
        headers["Accept"] = "application/vnd.api+json"
        headers["Content-Type"] = "application/vnd.api+json"
        headers["User-Agent"] = "Kitsu.py (https://github.com/SageTendo/kitsu.py)"
        kwargs["headers"] = headers

        __log__.debug("Request Headers: %s", headers)
        __log__.debug("Request URL: %s", url)

        async with self._session.get(url=url, **kwargs) as response:
            data = await response.json()

            if response.status == 200:
                return data

            if response.status == 400:
                raise BadRequest(response, data["errors"][0]["detail"])
            if response.status == 401:
                raise Unauthorized(response, data["error_description"])
            if response.status == 403:
                raise Forbidden(response, data["error_description"])
            if response.status == 404:
                raise NotFound(response, data["errors"][0]["detail"])

            raise HTTPException(response, await response.text(), response.status)

    async def authenticate(self, username: str, password: str) -> None:
        data = self.__add_client_info(
            {
                "grant_type": "password",
                "username": username,
                "password": password,
            }
        )
        response = await self._post(url=f"{AUTH_BASE}/token", data=data)

        self._token = response["access_token"]
        self._refresh_token = response["refresh_token"]
        created_at = datetime.fromtimestamp(response["created_at"])
        self._token_expires = created_at + timedelta(seconds=response["expires_in"])

    async def refresh_token(self) -> None:
        headers = {"Authorization": f"Bearer {self._token}"}
        data = self.__add_client_info(
            {
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            }
        )
        data = await self._post(url=f"{AUTH_BASE}/token", data=data, headers=headers)
        self._token = data["access_token"]
        self._refresh_token = data["refresh_token"]
        created_at = datetime.fromtimestamp(data["created_at"])
        self._token_expires = created_at + timedelta(seconds=data["expires_in"])

    async def get_anime(self, anime_id: int, *, include_nsfw: bool = False) -> Anime:
        """Get information of an anime by ID"""
        headers = {"Authorization": f"Bearer {self._token}"} if include_nsfw else {}
        data = await self._get(url=f"{BASE}/anime/{anime_id}", headers=headers)
        return Anime(payload=data["data"], client=self)

    async def get_anime_genres(self, anime_id: int, *, include_nsfw: bool = False) -> list[Genre]:
        """Get anime's genres"""
        headers = {"Authorization": f"Bearer {self._token}"} if include_nsfw else {}
        data = await self._get(url=f"{BASE}/anime/{anime_id}/genres", headers=headers)
        return [Genre(genre) for genre in data["data"]]

    async def search_anime(self, query: str, limit: int = 1, *, include_nsfw: bool = False) -> list[Anime]:
        """Search for an anime"""
        headers = {"Authorization": f"Bearer {self._token}"} if include_nsfw else {}
        data = await self._get(
            url=f"{BASE}/anime", params={"filter[text]": query, "page[limit]": str(limit)}, headers=headers
        )

        if not data["data"]:
            return []

        if len(data["data"]) == 1:
            return [Anime(data["data"][0], client=self)]
        return [Anime(anime, client=self) for anime in data["data"]]

    async def trending_anime(self, *, raw: bool = False) -> list[Anime]:
        """Get treding anime"""
        data = await self._get(f"{BASE}/trending/anime")
        if not data["data"]:
            return []
        return [Anime(anime, client=self) for anime in data["data"]]

    async def close(self) -> None:
        """Closes the internal http session"""
        return await self._session.close()
