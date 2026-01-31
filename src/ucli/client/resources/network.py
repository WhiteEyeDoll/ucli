from ucli.client.models.network import NetworkListModel, NetworkGetModel


class NetworksResource:

    def __init__(self, site_id: str, client: APIClientV1):
        self.site_id = site_id
        self.client = client

    def list(self, **filters) -> list[NetworkListModel]:
        data = self.client.request(
            "GET", f"/sites/{self.site_id}/networks", params=filters
        )

        return [NetworkListModel.model_validate(item) for item in data.get("data")]

    def get(self, network_id: str) -> list[NetworkGetModel]:
        data = self.client.request(
            "GET", f"/sites/{self.site_id}/networks/{network_id}"
        )

        return NetworkGetModel.model_validate(data)
