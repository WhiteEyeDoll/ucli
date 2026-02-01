from functools import cache

from ucli.client.client import APIClientV1
from ucli.client.models.options import ClientOptionsModel


@cache
def get_client(options: ClientOptionsModel) -> APIClientV1:

    client = APIClientV1(
        base_url=options.base_url,
        api_token=options.api_token,
        tls_verify=options.tls_verify,
    )

    return client
