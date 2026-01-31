from ucli.client.models.networks import NetworkList, NetworkGet
from ucli.client.resources.base import Resource


class Networks:

    def __init__(self, site_id: str, client: APIClientV1):
        self.site_id = site_id
        self.client = client

    def list(self, **filters) -> list[NetworkList]:
        data = self.client.request(
            "GET", f"/sites/{self.site_id}/networks", params=filters
        )

        return [NetworkList.model_validate(item) for item in data.get("data")]

    def get(self, network_id: str) -> list[NetworkGet]:
        data = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}"
        )

        return NetworkGet.model_validate(data)
