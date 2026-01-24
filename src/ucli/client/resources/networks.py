from ucli.client.models.networks import Network
from ucli.client.resources.site_resource import SiteResource

class Networks(SiteResource):

    def __init__(self, client, site_id):
        super().__init__(client)
        self.site_id = site_id

    def list(self):
        payload = self.client.request("GET", self.site_path("/networks"))
        
        return [Network.model_validate(item).model_dump() for item in payload.get("data")]
    