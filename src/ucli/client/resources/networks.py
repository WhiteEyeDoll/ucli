from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from ucli.client.models.network import Network

if TYPE_CHECKING:
    from ucli.client.client import APIClientV1


class NetworksResource:

    def __init__(self, site_id: UUID, client: APIClientV1):
        self.site_id = site_id
        self.client = client

    def list(self) -> Sequence[Network]:
        response = self.client.request("GET", f"/sites/{self.site_id}/networks")

        return [Network.model_validate(item) for item in response.get("data")]

    def get(self, network_id: UUID) -> Network:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}"
        )

        return Network.model_validate(response)
