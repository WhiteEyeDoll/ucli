from pydantic import BaseModel, model_validator, field_serializer
from typing import Optional
from typing_extensions import Self


class NetworkMetadata(BaseModel):
    origin: str


class NetworkDHCPGuarding(BaseModel):
    trustedDhcpServerIpAddresses: list[str]


class NetworkBase(BaseModel):
    name: str
    vlanId: int
    enabled: bool
    id: str
    management: str
    metadata: NetworkMetadata


class NetworkList(NetworkBase):
    deviceId: Optional[str] = None


class NetworkGet(NetworkBase):
    dhcpGuarding: Optional[NetworkDHCPGuarding] = None
