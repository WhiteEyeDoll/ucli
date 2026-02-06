from functools import cache
from types import TracebackType
from typing import Optional, Self, Type

import httpx

from ucli.client.models.options import ClientOptionsModel
from ucli.client.resources.sites import SitesResource


class APIClientV1:

    def __init__(self, options: ClientOptionsModel):

        self.options = options

        base_url = httpx.URL(str(self.options.base_url)).join(
            "proxy/network/integration/v1/"
        )

        self._client = httpx.Client(
            base_url=base_url,
            verify=self.options.verify_tls,
            timeout=10.0,
            headers={"X-API-KEY": self.options.api_key},
        )

    def request(self, method: str, path: str, **kwargs):

        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()

        try:
            return response.json()
        except ValueError as error:
            content_type = response.headers.get("Content-Type", "")
            body = response.text
            snippet = body[:200] if body else ""
            raise ValueError(
                "Expected JSON response but received non-JSON body. "
                f"status={response.status_code} content_type={content_type!r} "
                f"body_snippet={snippet!r}"
            ) from error

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "APIClientV1":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:

        _ = (exc_type, exc_value, traceback)

        self.close()

    @property
    def sites(self) -> SitesResource:
        return SitesResource(self)

    @classmethod
    @cache
    def get_client(cls, options: ClientOptionsModel) -> Self:

        return cls(options)
