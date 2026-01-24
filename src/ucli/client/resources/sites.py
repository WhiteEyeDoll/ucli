from ucli.client.resources.base import Resource
from ucli.client.models.sites import Site

class Sites(Resource):
    def list(self):
        payload = self.client.request("GET", "/sites")
        
        return [Site(**item) for item in payload.get("data", payload)]