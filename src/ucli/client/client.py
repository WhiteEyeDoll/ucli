import os
import httpx
from pydantic import BaseModel

from ucli.client.resources.sites import Sites
from ucli.client.resources.networks import Networks


class APIClient:
    
    def __init__(
        self,
        host: str,
        api_key: str,
        base_path: str = "proxy/network/integration/v1",
        verify_tls: bool = False,
    ):
        
        self.base_url = f"https://{host}/{base_path.lstrip("/")}".rstrip("/")

        self._client = httpx.Client(
            base_url=self.base_url,
            verify=verify_tls,
            timeout=10.0,
            headers={
                "X-API-KEY": api_key
            }
        )

    def request(self, method: str, path: str, **kwargs):
        
        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()

        return response.json()
    
    @property
    def sites(self) -> Sites:
        return Sites(self)
    
    def networks(self, site_id: str) -> Networks:
        return Networks(client=self, site_id=site_id)

def get_client() -> APIClient:

    host = os.getenv("UNIFI_HOST")
    api_key = os.getenv("UNIFI_API_KEY")
    base_path = os.getenv("UNIFI_BASE_PATH")
    
    return APIClient(
        host=host,
        base_path=base_path,
        api_key=api_key,
    )