from pydantic import BaseModel


class ClientOptionsModel(BaseModel):
    base_url: str
    api_token: str
    tls_verify: bool = True

    model_config = {"frozen": True}
