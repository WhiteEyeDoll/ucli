from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    IPvAnyAddress,
    IPvAnyNetwork,
    field_validator,
    model_validator,
)


class MetaDataBase(BaseModel):
    pass


class MetaDataUserDefined(MetaDataBase):
    origin: Literal["USER_DEFINED"]


class MetaDataSystemDefined(MetaDataBase):
    origin: Literal["SYSTEM_DEFINED"]


class MetaDataOrchestrated(MetaDataBase):
    origin: Literal["ORCHESTRATED"]


MetaData = Annotated[
    MetaDataUserDefined | MetaDataSystemDefined | MetaDataOrchestrated,
    Field(discriminator="origin"),
]


class DhcpGuarding(BaseModel):
    trustedDhcpServerIpAddresses: list[IPvAnyAddress]

    # Problematic behaviour in Unifi Network API.
    # Sometimes empty strings are returned in addition to IP addresses.
    # According to Unifi support these are meant as placeholders if there is less than three (3) defined addresses.
    # Remove empty strings before validating given values.

    @field_validator("trustedDhcpServerIpAddresses", mode="before")
    @classmethod
    def remove_empty_strings(cls, value):
        if isinstance(value, list):
            return [
                item
                for item in value
                if not (isinstance(item, str) and item.strip() == "")
            ]
        return value


class IpAddressRange(BaseModel):
    start: IPvAnyAddress
    stop: IPvAnyAddress


class PxeConfiguration(BaseModel):
    serverIpAddress: IPvAnyAddress
    filename: str


class IpAddressSelectorBase(BaseModel):
    pass


class IpAddressSelectorSingle(IpAddressSelectorBase):
    type: Literal["IP_ADDRESS"]
    value: IPvAnyAddress


class IpAddressSelectorRange(IpAddressSelectorBase):
    type: Literal["IP_ADDRESS_RANGE"]
    start: IPvAnyAddress
    stop: IPvAnyAddress

    @model_validator(mode="after")
    def validate_configuration(self):

        if int(self.start) > int(self.stop):
            raise ValueError("'start' must be <= 'stop'")

        return self


IpAddressSelector = Annotated[
    IpAddressSelectorSingle | IpAddressSelectorRange, Field(discriminator="type")
]


class RouterAdvertisement(BaseModel):
    priority: str


class NatOutboundIpAddressConfigurationBase(BaseModel):
    pass


class NatOutboundIpAddressAutoConfiguration(NatOutboundIpAddressConfigurationBase):
    type: Literal["AUTO"]
    wanInterfaceId: str
    ipAddressSelectionMode: str | None = Field(default=None)


class NatOutboundIpAddressStaticConfiguration(NatOutboundIpAddressConfigurationBase):
    type: Literal["STATIC"]
    wanInterfaceId: str
    ipAddressSelectors: IpAddressSelector | None = Field(default=None)


NatOutboundIpAddressConfiguration = Annotated[
    NatOutboundIpAddressAutoConfiguration | NatOutboundIpAddressStaticConfiguration,
    Field(discriminator="type"),
]


class Ipv4DhcpConfigurationBase(BaseModel):
    pass


class Ipv4DhcpServerConfiguration(Ipv4DhcpConfigurationBase):
    mode: Literal["SERVER"]
    ipAddressRange: IpAddressRange
    gatewayIpAddressOverride: IPvAnyAddress | None = Field(default=None)
    dnsServerIpAddressOverride: IPvAnyAddress | None = Field(default=None)
    leaseTimeSeconds: int
    domainName: str | None = Field(default=None)
    pingConflictDetectionEnabled: bool = Field(default=True)
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


class Ipv4DhcpRelayConfguration(Ipv4DhcpConfigurationBase):
    mode: Literal["RELAY"]
    dhcpServerIpAddresses: list[IPvAnyAddress]


Ipv4DhcpConfiguration = Annotated[
    Ipv4DhcpServerConfiguration | Ipv4DhcpRelayConfguration, Field(discriminator="mode")
]


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
    dhcpConfiguration: Ipv6DhcpConfiguration
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


class NetworkBase(BaseModel):
    id: UUID
    name: str
    enabled: bool
    vlanId: int
    metadata: MetaData
    dhcpGuarding: DhcpGuarding | None = Field(default=None)
    default: bool


class UnmanagedNetwork(NetworkBase):
    management: Literal["UNMANAGED"]


class GatewayManagedNetwork(NetworkBase):
    management: Literal["GATEWAY"]
    isolationEnabled: bool | None = Field(default=None)
    cellularBackupEnabled: bool | None = Field(default=None)
    zoneId: UUID | None = Field(default=None)
    internetAccessEnabled: bool | None = Field(default=None)
    mdnsForwardingEnabled: bool | None = Field(default=None)
    ipv4Configuration: Ipv4Configuration | None = Field(default=None)
    ipv6Configuration: Ipv6Configuration | None = Field(default=None)


class SwitchManagedNetwork(NetworkBase):
    management: Literal["SWITCH"]
    isolationEnabled: bool | None = Field(default=None)
    cellularBackupEnabled: bool | None = Field(default=None)
    deviceId: UUID | None = Field(default=None)
    ipv4Configuration: Ipv4Configuration | None = Field(default=None)


Network = Annotated[
    UnmanagedNetwork | GatewayManagedNetwork | SwitchManagedNetwork,
    Field(discriminator="management"),
]


class NetworkWriteBase(BaseModel):
    name: str
    enabled: bool = Field(default=True)
    vlanId: int
    dhcpGuarding: DhcpGuarding | None = Field(default=None)


class NetworkWriteUnmanaged(NetworkWriteBase):
    management: Literal["UNMANAGED"]


class NetworkWriteGatewayManaged(NetworkWriteBase):
    management: Literal["GATEWAY"]
    isolationEnabled: bool = Field(default=False)
    cellularBackupEnabled: bool = Field(default=False)
    zoneId: UUID | None = Field(default=None)
    internetAccessEnabled: bool = Field(default=True)
    mdnsForwardingEnabled: bool = Field(default=True)
    ipv4Configuration: Ipv4Configuration
    ipv6Configuration: Ipv6Configuration | None = Field(default=None)


class NetworkWriteSwitchManaged(NetworkWriteBase):
    management: Literal["SWITCH"]
    isolationEnabled: bool = Field(default=False)
    cellularBackupEnabled: bool = Field(default=False)
    deviceId: UUID
    ipv4Configuration: Ipv4Configuration


NetworkWrite = Annotated[
    NetworkWriteUnmanaged | NetworkWriteGatewayManaged | NetworkWriteSwitchManaged,
    Field(discriminator="management"),
]
