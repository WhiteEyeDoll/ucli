from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, IPvAnyAddress, IPvAnyNetwork, model_validator


class Metadata(BaseModel):
    origin: Literal["USER_DEFINED", "SYSTEM_DEFINED", "ORCHESTRATED"]


class DhcpGuarding(BaseModel):
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
    def validate_configuration(self):

        if self.type == "IP_ADDRESS":
            if self.value is None:
                raise ValueError("type='IP_ADDRESS' requires 'value'")
            if self.start is not None or self.stop is not None:
                raise ValueError("type='IP_ADDRESS' forbids 'start'/'stop'")
            return self

        if self.start is None or self.stop is None:
            raise ValueError("type='IP_ADDRESS_RANGE' requires both 'start' and 'stop'")

        if self.value is not None:
            raise ValueError("type='IP_ADDRESS_RANGE' forbids 'value'")

        if int(self.start) > int(self.stop):
            raise ValueError("'start' must be <= 'stop'")

        return self


class RouterAdvertisement(BaseModel):
    priority: str


class NatOutboundIpAddressConfiguration(BaseModel):
    type: Literal["AUTO", "STATIC"]
    wanInterfaceId: str
    ipAddressSelectionMode: str | None = Field(default=None)
    ipAddressSelectors: IpAddressSelector | None = Field(default=None)


class Ipv4DhcpConfiguration(BaseModel):
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
    dhcpConfiguration: Ipv4DhcpConfiguration


class Ipv6AddressSuffixRange(BaseModel):
    start: IPvAnyAddress
    stop: IPvAnyAddress

    @model_validator(mode="after")
    def validate_configuration(self):

        if self.start is None or self.stop is None:
            raise ValueError(
                "type='Ipv6AddressSuffixRange' requires both 'start' and 'stop'"
            )

        if int(self.start) > int(self.stop):
            raise ValueError("'start' must be <= 'stop'")

        return self


class Ipv6DhcpConfiguration(BaseModel):
    ipAddressSuffixRange: Ipv6AddressSuffixRange
    leaseTimeSeconds: int


class Ipv6ClientAddressAssignment(BaseModel):
    DhcpConfiguration: Ipv6DhcpConfiguration
    slaacEnabled: bool


class Ipv6Configuration(BaseModel):
    interfaceType: Literal["PREFIX_DELEGATION", "STATIC"]
    clientAddressAssignment: Ipv6ClientAddressAssignment
    routerAdvertisement: RouterAdvertisement | None = Field(default=None)
    dnsServerIpAddressOverride: list[IPvAnyAddress] | None = Field(default=None)
    additionalHostIpSubnets: list[IPvAnyNetwork] | None = Field(default=None)
    prefixDelegationWanInterfaceId: UUID | None = Field(default=None)


class NetworkReferenceResourceDetail(BaseModel):
    referenceId: UUID


class NetworkReferenceResource(BaseModel):
    resourceType: str
    referenceCount: int
    references: list[NetworkReferenceResourceDetail] | None = Field(default=None)


class Network(BaseModel):
    management: Literal["UNMANAGED", "GATEWAY", "SWITCH"]
    id: UUID
    name: str
    enabled: bool
    vlanId: int
    metadata: Metadata
    dhcpGuarding: DhcpGuarding | None = Field(default=None)
    isolationEnabled: bool | None = Field(default=None)
    cellularBackupEnabled: bool | None = Field(default=None)
    deviceId: UUID | None = Field(default=None)
    zoneId: UUID | None = Field(default=None)
    internetAccessEnabled: bool | None = Field(default=None)
    mdnsForwardingEnabled: bool | None = Field(default=None)
    ipv4Configuration: Ipv4Configuration | None = Field(default=None)
    ipv6Configuration: Ipv6Configuration | None = Field(default=None)


class NetworkCreate(BaseModel):
    management: Literal["UNMANAGED", "GATEWAY", "SWITCH"]
    name: str
    enabled: bool
    vlanId: int
    dhcpGuarding: DhcpGuarding | None = Field(default=None)
    isolationEnabled: bool | None = Field(default=None)
    deviceId: UUID | None = Field(default=None)
    cellularBackupEnabled: bool | None = Field(default=None)
    zoneId: UUID | None = Field(default=None)
    internetAccessEnabled: bool | None = Field(default=None)
    mdnsForwardingEnabled: bool | None = Field(default=None)
    ipv4Configuration: Ipv4Configuration | None = Field(default=None)
    ipv6Configuration: Ipv6Configuration | None = Field(default=None)


class NetworkUpdate(BaseModel):
    management: Literal["UNMANAGED", "GATEWAY", "SWITCH"]
    name: str
    enabled: bool
    vlanId: int
    dhcpGuarding: DhcpGuarding | None = Field(default=None)
    isolationEnabled: bool | None = Field(default=None)
    deviceId: UUID | None = Field(default=None)
    cellularBackupEnabled: bool | None = Field(default=None)
    zoneId: UUID | None = Field(default=None)
    internetAccessEnabled: bool | None = Field(default=None)
    mdnsForwardingEnabled: bool | None = Field(default=None)
    ipv4Configuration: Ipv4Configuration | None = Field(default=None)
    ipv6Configuration: Ipv6Configuration | None = Field(default=None)
