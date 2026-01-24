from ucli.client.resources.base import Resource
from ucli.client.resources.site_resource import SiteResource
from ucli.client.resources.networks import Networks
from ucli.client.models.sites import Site


class Sites(Resource):

    def __getitem__(self, site_id: str) -> "Site":
        return Site(self.client, site_id)
    
    def get_id(self, name: str) -> str:
        """Return the site_id for a given site name"""
        for site in self.list():
            if site.name == name:
                return site.id
        raise ValueError(f"No site found with name {name}")

    def list(self):
        payload = self.client.request("GET", "/sites")
        
        return [Site.model_validate(item) for item in payload.get("data")]

    
