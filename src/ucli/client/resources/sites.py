from ucli.client.resources.base import Resource
from ucli.client.resources.site_resource import SiteResource
from ucli.client.resources.networks import Networks
from ucli.client.models.sites import Site


class Sites(Resource):
    
    def get_id_by_name(self, name: str) -> str:
        """Return the id for a given site name"""
        for site in self.list():
            if site["name"] == name:
                return site["id"]
        raise ValueError(f"No site found with name {name}")

    def list(self):
        payload = self.client.request("GET", "/sites")
        
        return [Site.model_validate(item).model_dump() for item in payload.get("data")]

    
