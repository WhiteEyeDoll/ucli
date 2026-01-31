from pydantic import BaseModel, model_validator, field_serializer
from typing import Optional
from typing_extensions import Self

class NetworkMetadata(BaseModel):
    origin: str

class NetworkDHCPGuarding(BaseModel):
    trustedDhcpServerIpAddresses: list[str]

class NetworkBase(BaseModel):
    management: str
    id: str
    name: str
    enabled: bool
    vlanId: int
    metadata: NetworkMetadata

class NetworkList(NetworkBase):
    deviceId: Optional[str] = None
    
    
class NetworkGet(NetworkBase):
    dhcpGuarding: Optional[NetworkDHCPGuarding] = None


