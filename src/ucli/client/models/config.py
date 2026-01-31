from pydantic import BaseModel

class ClientOptions(BaseModel):
    base_url: str
    api_token: str
    tls_verify: bool = False
    