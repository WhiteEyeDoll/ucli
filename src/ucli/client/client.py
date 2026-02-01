from functools import cache
from typing import Self

import httpx

from ucli.client.models.options import ClientOptionsModel
from ucli.client.resources.site import SitesResource


class APIClientV1:

    def __init__(self, options: ClientOptionsModel):

        self.options = options

        self._client = httpx.Client(
            base_url=f"{self.options.base_url}proxy/network/integration/v1",
            verify=self.options.tls_verify,
            timeout=10.0,
            headers={"X-API-KEY": self.options.api_token},
        )

    def request(self, method: str, path: str, **kwargs):

        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()

        return response.json()

    @property
    def sites(self) -> SitesResource:
        return SitesResource(self)

    @classmethod
    @cache
    def get_client(cls, options: ClientOptionsModel) -> Self:

        return cls(options)
