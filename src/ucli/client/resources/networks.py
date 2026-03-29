from __future__ import annotations

import json
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import TypeAdapter
from ucli.client.models.network import (
    Network,
    NetworkReferenceResource,
    NetworkWrite,
)

if TYPE_CHECKING:
    from ucli.client.client import APIClientV1


network_adapter = TypeAdapter(Network)


class NetworksResource:

    def __init__(self, site_id: UUID, client: APIClientV1):
        self.site_id = site_id
        self.client = client

    def list(self) -> list[Network]:
        response = self.client.request("GET", f"/sites/{self.site_id}/networks")

        data = response.get("data", [])
        if data is None:
            data = []
        if not isinstance(data, list):
            raise TypeError(f"Expected list data for networks, got {type(data)}")

        network_list = [network_adapter.validate_python(item) for item in data]

        return network_list

    def get(self, network_id: UUID) -> Network:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}"
        )

        network = network_adapter.validate_python(response)

        return network

    def create(self, network_configuration: NetworkWrite) -> Network:

        json_data = network_configuration.model_dump(mode="json", exclude_none=True)
        request_body = json.dumps(json_data)

        response = self.client.request(
            "POST",
            f"/sites/{self.site_id}/networks",
            content=request_body,
            headers={"Content-Type": "application/json"},
        )

        network = network_adapter.validate_python(response)

        return network

    def update(self, network_id: UUID, network_configuration: NetworkWrite) -> Network:

        json_data = network_configuration.model_dump(mode="json", exclude_none=True)
        request_body = json.dumps(json_data)

        response = self.client.request(
            "PUT",
            f"/sites/{self.site_id}/networks/{network_id}",
            content=request_body,
            headers={"Content-Type": "application/json"},
        )

        network = network_adapter.validate_python(response)

        return network

    def delete(self, network_id: UUID):
        response = self.client.request(
            "DELETE", f"/sites/{self.site_id}/networks/{network_id}"
        )

        return response

    def get_references(self, network_id: UUID) -> list[NetworkReferenceResource]:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}/references"
        )

        data = response.get("referenceResources", [])
        if data is None:
            data = []
        if not isinstance(data, list):
            raise TypeError(
                f"Expected list data for network references, got {type(data)}"
            )

        network_reference_list = [
            NetworkReferenceResource.model_validate(item) for item in data
        ]

        return network_reference_list
