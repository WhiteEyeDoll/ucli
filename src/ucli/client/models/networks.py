from pydantic import BaseModel, model_validator
from typing import Optional
from typing_extensions import Self

class NetworkMetadata(BaseModel):
    origin: str

class Network(BaseModel):
    management: str
    id: str
    name: str
    enabled: bool
    vlanId: int
    metadata: NetworkMetadata
    deviceId: Optional[str] = None

    @model_validator(mode="after")
    def check_managed_type_for_device_id(self) -> Self:
        if self.management != "SWITCH" and self.deviceId != None:
            raise ValueError("deviceId can only be set when management type is SWITCH")
        return self