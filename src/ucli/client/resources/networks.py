from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from ucli.client.models.network import (
    Network,
    NetworkCreate,
    NetworkReferenceResource,
    NetworkUpdate,
)

if TYPE_CHECKING:
    from ucli.client.client import APIClientV1


class NetworksResource:

    def __init__(self, site_id: UUID, client: APIClientV1):
        self.site_id = site_id
        self.client = client

    def list(self) -> Sequence[Network]:
        response = self.client.request("GET", f"/sites/{self.site_id}/networks")

        network_list = [
            Network.model_validate(item) for item in response.get("data", [])
        ]

        return network_list

    def get(self, network_id: UUID) -> Network:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}"
        )

        network = Network.model_validate(response)

        return network

    def create(self, network_configuration: NetworkCreate) -> Network:

        json_data = network_configuration.model_dump(mode="json")

        response = self.client.request(
            "POST",
            f"/sites/{self.site_id}/networks",
            json=json_data,
        )

        network = Network.model_validate(response)

        return network

    def update(self, network_id: UUID, network_configuration: NetworkUpdate) -> Network:

        json_data = network_configuration.model_dump(mode="json")

        response = self.client.request(
            "PUT",
            f"/sites/{self.site_id}/networks/{network_id}",
            json=json_data,
        )

        network = Network.model_validate(response)

        return network

    def delete(self, network_id: UUID):
        response = self.client.request(
            "DELETE", f"/sites/{self.site_id}/networks/{network_id}"
        )

        return response

    def get_references(self, network_id: UUID) -> Sequence[NetworkReferenceResource]:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/{network_id}/networks/references"
        )

        network_reference_list = [
            NetworkReferenceResource.model_validate(item)
            for item in response.get("referenceResources", [])
        ]

        return network_reference_list
