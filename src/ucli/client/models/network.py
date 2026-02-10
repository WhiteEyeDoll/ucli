from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, IPvAnyAddress, IPvAnyNetwork, model_validator


class NetworkMetadata(BaseModel):
    origin: Literal["USER_DEFINED", "SYSTEM_DEFINED", "ORCHESTRATED"]


class NetworkDhcpGuarding(BaseModel):
    # Bug in Unifi Network API.
    # Sometimes empty strings are returned in addtion to IP addresses.
    trustedDhcpServerIpAddresses: list[IPvAnyAddress | str]


class IpAddressRange(BaseModel):
    # Unifi Network API lists these as required but does not currently return them.
    # Mark as optional to work around this bug.
    start: IPvAnyAddress | None = Field(default=None)
    stop: IPvAnyAddress | None = Field(default=None)


class PxeConfiguration(BaseModel):
    serverIpAddress: IPvAnyAddress
    filename: str


class IpAddressSelector(BaseModel):
    type: Literal["IP_ADDRESS", "IP_ADDRESS_RANGE"]
    value: IPvAnyAddress | None = Field(default=None)
    start: IPvAnyAddress | None = Field(default=None)
    stop: IPvAnyAddress | None = Field(default=None)

    @model_validator(mode="after")
    def check_mutual_exclusion(self):

        # ---- IP_ADDRESS_RANGE ----
        if self.type == "IP_ADDRESS":
            if self.value is None:
                raise ValueError("type='IP_ADDRESS' requires 'value'")
            if self.start is not None or self.stop is not None:
                raise ValueError("type='IP_ADDRESS' forbids 'start'/'stop'")
            return self

        # ---- IP_ADDRESS_RANGE ----
        if self.start is None or self.stop is None:
            raise ValueError("type='IP_ADDRESS_RANGE' requires both 'start' and 'stop'")

        if self.value is not None:
            raise ValueError("type='IP_ADDRESS_RANGE' forbids 'value'")

        if int(self.start) > int(self.stop):
            raise ValueError("'start' must be <= 'stop'")

        return self


class NatOutboundIpAddressConfiguration(BaseModel):
    type: Literal["AUTO", "STATIC"]
    wanInterfaceId: str
    ipAddressSelectionMode: str | None = Field(default=None)
    ipAddressSelectors: IpAddressSelector | None = Field(default=None)


class DhcpConfiguration(BaseModel):
    mode: Literal["SERVER", "RELAY"]
    ipAddressRange: IpAddressRange | None = Field(default=None)
    gatewayIpAddressOverride: IPvAnyAddress | None = Field(default=None)
    dnsServerIpAddressOverride: IPvAnyAddress | None = Field(default=None)
    leasetimeSeconds: int | None = Field(default=None)
    domainName: str | None = Field(default=None)
    pingConflictDetectionEnabled: bool | None = Field(default=None)
    pxeConfiguration: PxeConfiguration | None = Field(default=None)
    ntpServerIpAddress: list[IPvAnyAddress] | None = Field(default=None)
    option43Value: str | None = Field(default=None)
    tftpServerAddress: IPvAnyAddress | None = Field(default=None)
    timeOffsetSeconds: int | None = Field(default=None)
    wpadUrl: str | None = Field(default=None)
    winsServerIpAddresses: list[IPvAnyAddress] | None = Field(default=None)
    natOutboundIpAddressConfiguration: NatOutboundIpAddressConfiguration | None = Field(
        default=None
    )


class Ipv4Configuration(BaseModel):
    autoScaleEnabled: bool
    hostIpAddress: IPvAnyAddress
    prefixLength: int
    additionalHostIpSubnets: list[IPvAnyNetwork] | None = Field(default=None)
    dhcpConfiguration: DhcpConfiguration


class Network(BaseModel):
    name: str
    vlanId: int
    enabled: bool
    id: UUID
    management: Literal["UNMANAGED", "GATEWAY", "SWITCH"]
    metadata: NetworkMetadata
    deviceId: UUID | None = Field(default=None)
    dhcpGuarding: NetworkDhcpGuarding | None = Field(default=None)
    isolationEnabled: bool | None = Field(default=None)
    cellularBackupEnabled: bool | None = Field(default=None)
    zoneId: UUID | None = Field(default=None)
    internetAccessEnabled: bool | None = Field(default=None)
    mdnsForwardingEnabled: bool | None = Field(default=None)
    ipv4Configuration: Ipv4Configuration | None = Field(default=None)
