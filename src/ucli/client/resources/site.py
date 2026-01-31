from ucli.client.resources.network import NetworksResource
from ucli.client.models.site import SiteModel


class SiteResource:
    def __init__(self, model: SiteModel, client: "APIClientV1"):
        self.model = model
        self.client = client
        self.networks = NetworksResource(self.model.id, client)

    @property
    def id(self):
        return self.model.id

    @property
    def name(self):
        return self.model.name


class SitesResource:

    def __init__(self, client: APIClientV1):
        self.client = client

    def list(self):
        data = self.client.request("GET", "/sites")

        return [SiteModel.model_validate(item) for item in data.get("data")]

    def get(self, site_id: str) -> SiteModel:
        for site in self.list():
            if site.id == site_id:
                return SiteResource(SiteModel.model_validate(site), self.client)
        raise ValueError(f"No site found with name {site_id}")
