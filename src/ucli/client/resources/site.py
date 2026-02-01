from ucli.client.resources.network import NetworksResource
from ucli.client.models.site import SiteModel
from uuid import UUID


class SiteResource:
    def __init__(self, model: SiteModel, client: "APIClientV1"):
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

    def list(self) -> list[SiteModel]:
        response = self.client.request("GET", "/sites")

        return [SiteModel.model_validate(item) for item in response.get("data")]

    def get(self, site_id: UUID) -> SiteModel:
        for site in self.list():
            if site.id == site_id:
                return SiteResource(SiteModel.model_validate(site), self.client)
        raise ValueError(f"No site found with id {site_id}")
