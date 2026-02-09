from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, IPvAnyAddress, IPvAnyNetwork, model_validator


class NetworkMetadataModel(BaseModel):
    origin: Literal["USER_DEFINED", "SYSTEM_DEFINED", "ORCHESTRATED"]


class NetworkDhcpGuardingModel(BaseModel):
    # Bug in Unifi Network API.
    # Sometimes empty strings are returned in addtion to IP addresses.
    trustedDhcpServerIpAddresses: list[IPvAnyAddress | str]


class IpAddressRangeModel(BaseModel):
    # Unifi Network API lists these as required but does not currently return them.
    # Mark as optional to work around this bug.
    start: Optional[IPvAnyAddress] = None
    stop: Optional[IPvAnyAddress] = None


class PxeConfigurationModel(BaseModel):
    serverIpAddress: IPvAnyAddress
    filename: str


class IpAddressSelectorModel(BaseModel):
    type: Literal["IP_ADDRESS", "IP_ADDRESS_RANGE"]
    value: Optional[IPvAnyAddress] = None
    start: Optional[IPvAnyAddress] = None
    stop: Optional[IPvAnyAddress] = None

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
    ipAddressSelectionMode: Optional[str] = None
    ipAddressSelectors: Optional[IpAddressSelectorModel] = None


class DhcpConfigurationModel(BaseModel):
    mode: Literal["SERVER", "RELAY"]
    ipAddressRange: Optional[IpAddressRangeModel] = None
    gatewayIpAddressOverride: Optional[IPvAnyAddress] = None
    dnsServerIpAddressOverride: Optional[IPvAnyAddress] = None
    leasetimeSeconds: Optional[int] = None
    domainName: Optional[str] = None
    pingConflictDetectionEnabled: Optional[bool] = None
    pxeConfiguration: Optional[PxeConfigurationModel] = None
    ntpServerIpAddress: Optional[list[IPvAnyAddress]] = None
    option43Value: Optional[str] = None
    tftpServerAddress: Optional[IPvAnyAddress] = None
    timeOffsetSeconds: Optional[int] = None
    wpadUrl: Optional[str] = None
    winsServerIpAddresses: Optional[list[IPvAnyAddress]] = None
    natOutboundIpAddressConfiguration: Optional[
        NatOutboundIpAddressConfigurationModel
    ] = None


class Ipv4ConfigurationModel(BaseModel):
    autoScaleEnabled: bool
    hostIpAddress: IPvAnyAddress
    prefixLength: int
    additionalHostIpSubnets: Optional[list[IPvAnyNetwork]] = None
    dhcpConfiguration: DhcpConfigurationModel


class NetworkBaseModel(BaseModel):
    name: str
    vlanId: int
    enabled: bool
    id: UUID
    management: Literal["UNMANAGED", "GATEWAY", "SWITCH"]
    metadata: NetworkMetadataModel


class NetworkListModel(NetworkBaseModel):
    deviceId: Optional[UUID] = None


class NetworkGetModel(NetworkBaseModel):
    dhcpGuarding: Optional[NetworkDhcpGuardingModel] = None
    isolationEnabled: Optional[bool] = None
    cellularBackupEnabled: Optional[bool] = None
    zoneId: Optional[UUID] = None
    internetAccessEnabled: Optional[bool] = None
    mdnsForwardingEnabled: Optional[bool] = None
    ipv4Configuration: Optional[Ipv4ConfigurationModel] = None
