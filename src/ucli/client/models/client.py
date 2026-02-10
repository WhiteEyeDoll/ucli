from pydantic import BaseModel, HttpUrl


class ClientOptions(BaseModel):
    base_url: HttpUrl
    api_key: str
    verify_tls: bool = True

    model_config = {"frozen": True}
