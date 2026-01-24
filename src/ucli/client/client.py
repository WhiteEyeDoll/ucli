import os
import httpx
from pydantic import BaseModel

from ucli.client.resources.sites import Sites


class APIClient:
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        verify_tls: bool = False,
    ):
        
        self.base_url = base_url.rstrip("/")

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
    

def get_client() -> APIClient:
    api_key = os.getenv("UNIFI_API_KEY", "sk_demo")
    base_url = os.getenv("UNIFI_BASE_URL", "https://api.ui.com/v1")
    return APIClient(api_key=api_key, base_url=base_url)