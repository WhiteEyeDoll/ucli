from pydantic import BaseModel, HttpUrl


class ClientOptionsModel(BaseModel):
    base_url: HttpUrl
    api_token: str
    tls_verify: bool = True

    model_config = {"frozen": True}
