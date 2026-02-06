from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from ucli.client.models.site import SiteModel
from ucli.client.resources.networks import NetworksResource

if TYPE_CHECKING:
    from ucli.client.client import APIClientV1


class SiteResource:
    def __init__(self, model: SiteModel, client: APIClientV1):
        self.model = model
        self.client = client
        self.networks = NetworksResource(self.model.id, client)

    @property
    def id(self) -> UUID:
        return self.model.id

    @property
    def name(self) -> str:
        return self.model.name


class SitesResource:

    def __init__(self, client: APIClientV1):
        self.client = client

    def list(self) -> Sequence[SiteModel]:
        response = self.client.request("GET", "/sites")

        data = response.get("data", [])
        if data is None:
            data = []
        if not isinstance(data, list):
            raise TypeError(f"Expected list data for sites, got {type(data)}")

        return [SiteModel.model_validate(item) for item in data]

    def get(self, site_id: UUID) -> SiteResource:
        for site in self.list():
            if site.id == site_id:
                return SiteResource(site, self.client)
        raise ValueError(f"No site found with id {site_id}")
