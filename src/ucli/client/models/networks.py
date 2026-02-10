from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, IPvAnyAddress, IPvAnyNetwork, model_validator


class NetworkMetadataModel(BaseModel):
    origin: Literal["USER_DEFINED", "SYSTEM_DEFINED", "ORCHESTRATED"]


class NetworkDhcpGuardingModel(BaseModel):
    # Bug in Unifi Network API.
    # Sometimes empty strings are returned in addtion to IP addresses.
    trustedDhcpServerIpAddresses: list[IPvAnyAddress | str]


class IpAddressRangeModel(BaseModel):
    # Unifi Network API lists these as required but does not currently return them.
    # Mark as optional to work around this bug.
    start: IPvAnyAddress | None = Field(default=None)
    stop: IPvAnyAddress | None = Field(default=None)


class PxeConfigurationModel(BaseModel):
    serverIpAddress: IPvAnyAddress
    filename: str


class IpAddressSelectorModel(BaseModel):
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

        if self.start.version != self.stop.version:
            raise ValueError(
                "'start' and 'stop' must be the same IP version (v4 or v6)"
            )

        if int(self.start) > int(self.stop):
            raise ValueError("'start' must be <= 'stop'")

        return self


class NatOutboundIpAddressConfigurationModel(BaseModel):
    type: Literal["AUTO", "STATIC"]
    wanInterfaceId: str
    ipAddressSelectionMode: str | None = Field(default=None)
    ipAddressSelectors: IpAddressSelectorModel | None = Field(default=None)


class DhcpConfigurationModel(BaseModel):
    mode: Literal["SERVER", "RELAY"]
    ipAddressRange: IpAddressRangeModel | None = Field(default=None)
    gatewayIpAddressOverride: IPvAnyAddress | None = Field(default=None)
    dnsServerIpAddressOverride: IPvAnyAddress | None = Field(default=None)
    leasetimeSeconds: int | None = Field(default=None)
    domainName: str | None = Field(default=None)
    pingConflictDetectionEnabled: bool | None = Field(default=None)
    pxeConfiguration: PxeConfigurationModel | None = Field(default=None)
    ntpServerIpAddress: list[IPvAnyAddress] | None = Field(default=None)
    option43Value: str | None = Field(default=None)
    tftpServerAddress: IPvAnyAddress | None = Field(default=None)
    timeOffsetSeconds: int | None = Field(default=None)
    wpadUrl: str | None = Field(default=None)
    winsServerIpAddresses: list[IPvAnyAddress] | None = Field(default=None)
    natOutboundIpAddressConfiguration: NatOutboundIpAddressConfigurationModel | None = (
        Field(default=None)
    )


class Ipv4ConfigurationModel(BaseModel):
    autoScaleEnabled: bool
    hostIpAddress: IPvAnyAddress
    prefixLength: int
    additionalHostIpSubnets: list[IPvAnyNetwork] | None = Field(default=None)
    dhcpConfiguration: DhcpConfigurationModel


class NetworkBaseModel(BaseModel):
    name: str
    vlanId: int
    enabled: bool
    id: UUID
    management: Literal["UNMANAGED", "GATEWAY", "SWITCH"]
    metadata: NetworkMetadataModel


class NetworkListModel(NetworkBaseModel):
    deviceId: UUID | None = Field(default=None)


class NetworkGetModel(NetworkBaseModel):
    dhcpGuarding: NetworkDhcpGuardingModel | None = Field(default=None)
    isolationEnabled: bool | None = Field(default=None)
    cellularBackupEnabled: bool | None = Field(default=None)
    zoneId: UUID | None = Field(default=None)
    internetAccessEnabled: bool | None = Field(default=None)
    mdnsForwardingEnabled: bool | None = Field(default=None)
    ipv4Configuration: Ipv4ConfigurationModel | None = Field(default=None)
