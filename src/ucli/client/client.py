import httpx
from ucli.client.resources.sites import Sites
from ucli.client.resources.networks import Networks


class APIClientV1:

    def __init__(
        self,
        base_url: str,
        api_token: str,
        tls_verify: bool = True,
    ):

        base_url = base_url.rstrip("/")
        self.base_url = f"{base_url}/proxy/network/integration/v1"

        self._client = httpx.Client(
            base_url=self.base_url,
            verify=tls_verify,
            timeout=10.0,
            headers={"X-API-KEY": api_token},
        )

    def request(self, method: str, path: str, **kwargs):

        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()

        return response.json()

    @property
    def sites(self) -> Sites:
        return Sites(self)
