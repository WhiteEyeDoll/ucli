from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING
from uuid import UUID

from ucli.client.models.site import Site
from ucli.client.resources.networks import NetworksResource

if TYPE_CHECKING:
    from ucli.client.client import APIClientV1


class SiteResource:
    def __init__(self, model: Site, client: APIClientV1):
        self.model = model
        self.client = client

    @property
    def id(self) -> UUID:
        return self.model.id

    @property
    def name(self) -> str:
        return self.model.name

    @cached_property
    def networks(self) -> NetworksResource:
        return NetworksResource(self.model.id, self.client)


class SitesResource:

    def __init__(self, client: APIClientV1):
        self.client = client

    def list(self) -> list[Site]:
        response = self.client.request("GET", "/sites")

        data = response.get("data", [])
        if data is None:
            data = []
        if not isinstance(data, list):
            raise TypeError(f"Expected list data for sites, got {type(data)}")

        return [Site.model_validate(item) for item in data]

    def get(self, site_id: UUID) -> SiteResource:
        # There is no separate /sites/{site_id} endpoint so list() has to be used here.
        for site in self.list():
            if site.id == site_id:
                return SiteResource(site, self.client)
        raise ValueError(f"No site found with id {site_id}")
