from ucli.client.models.networks import NetworkList, NetworkGet
from ucli.client.resources.site_resource import SiteResource


class Networks(SiteResource):

    def __init__(self, client, site_id):
        super().__init__(client)
        self.site_id = site_id

    def get_id_by_name(self, name: str) -> str:
        """Return the id for a given network name"""
        for network in self.list():
            if network.name == name:
                return network.id
        raise ValueError(f"No network found with name {name}")

    def list(self):
        payload = self.client.request("GET", self.site_path("/networks"))

        return [NetworkList.model_validate(item) for item in payload.get("data")]

    def get(self, id):
        payload = self.client.request("GET", self.site_path(f"/networks/{id}"))

        return NetworkGet.model_validate(payload)
