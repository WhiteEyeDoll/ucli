from ucli.client.client import APIClientV1
from ucli.client.models.config import ClientOptionsModel

_client_cache: APIClientV1 | None = None


def get_client(options: ClientOptionsModel) -> APIClientV1:
    global _client_cache
    if _client_cache is not None:
        return _client_cache

    client = APIClientV1(
        base_url=options.base_url,
        api_token=options.api_token,
        tls_verify=options.tls_verify,
    )
    _client_cache = client
    return client
