from ucli.client.resources.base import Resource
from ucli.client.resources.site_resource import SiteResource
from ucli.client.resources.networks import Networks
from ucli.client.models.sites import SiteModel


class Site:
    def __init__(self, model: SiteModel, client: "APIClientV1"):
        self.model = model
        self.client = client
        self.networks = Networks(self.model.id, client)

    @property
    def id(self):
        return self.model.id

    @property
    def name(self):
        return self.model.name


class Sites:

    def __init__(self, client: APIClientV1):
        self.client = client

    def list(self):
        data = self.client.request("GET", "/sites")

        return [SiteModel.model_validate(item) for item in data.get("data")]

    def get(self, site_id: str) -> SiteModel:
        for site in self.list():
            if site.id == site_id:
                return Site(SiteModel.model_validate(site), self.client)
        raise ValueError(f"No site found with name {site_id}")
