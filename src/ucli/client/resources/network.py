from ucli.client.models.network import NetworkListModel, NetworkGetModel
from uuid import UUID


class NetworksResource:

    def __init__(self, site_id: str, client: APIClientV1):
        self.site_id = site_id
        self.client = client

    def list(self) -> list[NetworkListModel]:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/networks", params=filters
        )

        return [NetworkListModel.model_validate(item) for item in response.get("data")]

    def get(self, network_id: UUID) -> NetworkGetModel:
        response = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}"
        )

        return NetworkGetModel.model_validate(response)
