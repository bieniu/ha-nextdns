"""The NextDNS component."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from aiohttp.client_exceptions import ClientConnectorError
import async_timeout
from nextdns import (
    AnalyticsDnssec,
    AnalyticsEncryption,
    AnalyticsIpVersions,
    AnalyticsProtocols,
    AnalyticsStatus,
    ApiError,
    ConnectionStatus,
    InvalidApiKeyError,
    NextDns,
    Profile,
)
from nextdns.model import NextDnsData

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_CONNECTION,
    ATTR_DNSSEC,
    ATTR_ENCRYPTION,
    ATTR_IP_VERSIONS,
    ATTR_PROFILE,
    ATTR_PROTOCOLS,
    ATTR_STATUS,
    CONF_PROFILE_ID,
    CONF_PROFILE_NAME,
    DOMAIN,
    UPDATE_INTERVAL_ANALYTICS,
    UPDATE_INTERVAL_CONNECTION,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary_sensor", "button", "sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NextDNS as config entry."""
    api_key = entry.data[CONF_API_KEY]
    profile_id = entry.data[CONF_PROFILE_ID]
    profile_name = entry.data[CONF_PROFILE_NAME]

    websession = async_get_clientsession(hass)
    try:
        with async_timeout.timeout(10):
            nextdns = await NextDns.create(websession, api_key)
    except (ApiError, ClientConnectorError, asyncio.TimeoutError) as err:
        raise ConfigEntryNotReady from err

    connection_coordinator = NextDnsConnectionUpdateCoordinator(
        hass, nextdns, profile_id, profile_name, UPDATE_INTERVAL_CONNECTION
    )
    dnssec_coordinator = NextDnsDnssecUpdateCoordinator(
        hass, nextdns, profile_id, profile_name, UPDATE_INTERVAL_ANALYTICS
    )
    encryption_coordinator = NextDnsEncryptionUpdateCoordinator(
        hass, nextdns, profile_id, profile_name, UPDATE_INTERVAL_ANALYTICS
    )
    ip_versions_coordinator = NextDnsIpVersionsUpdateCoordinator(
        hass, nextdns, profile_id, profile_name, UPDATE_INTERVAL_ANALYTICS
    )
    profile_coordinator = NextDnsProfileUpdateCoordinator(
        hass, nextdns, profile_id, profile_name, UPDATE_INTERVAL_CONNECTION
    )
    protocols_coordinator = NextDnsProtocolsUpdateCoordinator(
        hass, nextdns, profile_id, profile_name, UPDATE_INTERVAL_ANALYTICS
    )
    status_coordinator = NextDnsStatusUpdateCoordinator(
        hass, nextdns, profile_id, profile_name, UPDATE_INTERVAL_ANALYTICS
    )

    await asyncio.gather(
        connection_coordinator.async_config_entry_first_refresh(),
        dnssec_coordinator.async_config_entry_first_refresh(),
        encryption_coordinator.async_config_entry_first_refresh(),
        ip_versions_coordinator.async_config_entry_first_refresh(),
        profile_coordinator.async_config_entry_first_refresh(),
        protocols_coordinator.async_config_entry_first_refresh(),
        status_coordinator.async_config_entry_first_refresh(),
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id][ATTR_CONNECTION] = connection_coordinator
    hass.data[DOMAIN][entry.entry_id][ATTR_DNSSEC] = dnssec_coordinator
    hass.data[DOMAIN][entry.entry_id][ATTR_ENCRYPTION] = encryption_coordinator
    hass.data[DOMAIN][entry.entry_id][ATTR_IP_VERSIONS] = ip_versions_coordinator
    hass.data[DOMAIN][entry.entry_id][ATTR_PROFILE] = profile_coordinator
    hass.data[DOMAIN][entry.entry_id][ATTR_PROTOCOLS] = protocols_coordinator
    hass.data[DOMAIN][entry.entry_id][ATTR_STATUS] = status_coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class NextDnsUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NextDNS data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        nextdns: NextDns,
        profile_id: str,
        profile_name: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.nextdns = nextdns
        self.profile_id = profile_id
        self.profile_name = profile_name
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, str(profile_id))},
            name=profile_name,
            manufacturer="NextDNS",
            entry_type=DeviceEntryType.SERVICE,
        )

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> NextDnsData:
        """Update data via library."""
        raise NotImplementedError("Update method not implemented")


class NextDnsStatusUpdateCoordinator(NextDnsUpdateCoordinator):
    """Class to manage fetching NextDNS analytics status data from API."""

    async def _async_update_data(self) -> AnalyticsStatus:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.get_analytics_status(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err


class NextDnsDnssecUpdateCoordinator(NextDnsUpdateCoordinator):
    """Class to manage fetching NextDNS analytics Dnssec data from API."""

    async def _async_update_data(self) -> AnalyticsDnssec:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.get_analytics_dnssec(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err


class NextDnsEncryptionUpdateCoordinator(NextDnsUpdateCoordinator):
    """Class to manage fetching NextDNS analytics encryption data from API."""

    async def _async_update_data(self) -> AnalyticsEncryption:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.get_analytics_encryption(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err


class NextDnsIpVersionsUpdateCoordinator(NextDnsUpdateCoordinator):
    """Class to manage fetching NextDNS analytics IP versions data from API."""

    async def _async_update_data(self) -> AnalyticsIpVersions:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.get_analytics_ip_versions(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err


class NextDnsProtocolsUpdateCoordinator(NextDnsUpdateCoordinator):
    """Class to manage fetching NextDNS analytics protocols data from API."""

    async def _async_update_data(self) -> AnalyticsProtocols:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.get_analytics_protocols(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err


class NextDnsConnectionUpdateCoordinator(NextDnsUpdateCoordinator):
    """Class to manage fetching NextDNS connection data from API."""

    async def _async_update_data(self) -> ConnectionStatus:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.connection_status(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err


class NextDnsProfileUpdateCoordinator(NextDnsUpdateCoordinator):
    """Class to manage fetching NextDNS connection data from API."""

    async def _async_update_data(self) -> Profile:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.get_profile(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err
