from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from ucli.client.models.network import NetworkGetModel, NetworkListModel

if TYPE_CHECKING:
    from ucli.client.client import APIClientV1


class NetworksResource:

    def __init__(self, site_id: UUID, client: APIClientV1):
        self.site_id = site_id
        self.client = client

    def list(self) -> Sequence[NetworkListModel]:
        response = self.client.request("GET", f"/sites/{self.site_id}/networks")

        data = response.get("data", [])
        if data is None:
            data = []
        if not isinstance(data, list):
            raise TypeError(f"Expected list data for networks, got {type(data)}")

        return [NetworkListModel.model_validate(item) for item in data]

    def get(self, network_id: UUID) -> NetworkGetModel:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}"
        )

        return NetworkGetModel.model_validate(response)
