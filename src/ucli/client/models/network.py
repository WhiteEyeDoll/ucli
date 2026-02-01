from pydantic import BaseModel, model_validator, field_serializer
from typing import Optional
from uuid import UUID


class NetworkMetadataModel(BaseModel):
    origin: str


class NetworkDHCPGuardingModel(BaseModel):
    trustedDhcpServerIpAddresses: list[str]


class NetworkBaseModel(BaseModel):
    name: str
    vlanId: int
    enabled: bool
    id: UUID
    management: str
    metadata: NetworkMetadataModel


class NetworkListModel(NetworkBaseModel):
    deviceId: Optional[str] = None


class NetworkGetModel(NetworkBaseModel):
    dhcpGuarding: Optional[NetworkDHCPGuardingModel] = None
