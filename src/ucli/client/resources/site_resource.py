from ucli.client.resources.base import Resource


class SiteResource(Resource):
    def __init__(self, client):
        super().__init__(client)

    def site_path(self, path: str) -> str:
        return f"{self.client.base_url}/sites/{self.site_id}{path}"
