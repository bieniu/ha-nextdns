"""The NextDNS component."""
from __future__ import annotations

import asyncio
import logging

from aiohttp.client_exceptions import ClientConnectorError
import async_timeout
from nextdns import (
    AllAnalytics,
    ApiError,
    ConnectionStatus,
    InvalidApiKeyError,
    NextDns,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ANALYTICS_UPDATE_INTERVAL,
    CONF_PROFILE_ID,
    CONF_PROFILE_NAME,
    DOMAIN,
    STATUS_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary_sensor", "button", "sensor"]


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

    analytics_coordinator = NextDnsAnalyticsDataUpdateCoordinator(
        hass, nextdns, profile_id, profile_name
    )
    status_coordinator = NextDnsStatusDataUpdateCoordinator(
        hass, nextdns, profile_id, profile_name
    )
    await analytics_coordinator.async_config_entry_first_refresh()
    await status_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id]["analytics"] = analytics_coordinator
    hass.data[DOMAIN][entry.entry_id]["status"] = status_coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class NextDnsAnalyticsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NextDNS data API."""

    def __init__(
        self, hass: HomeAssistant, nextdns: NextDns, profile_id: str, profile_name: str
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

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=ANALYTICS_UPDATE_INTERVAL
        )

    async def _async_update_data(self) -> AllAnalytics:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.get_all_analytics(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err


class NextDnsStatusDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NextDNS data API."""

    def __init__(
        self, hass: HomeAssistant, nextdns: NextDns, profile_id: str, profile_name: str
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

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=STATUS_UPDATE_INTERVAL
        )

    async def _async_update_data(self) -> ConnectionStatus:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                return await self.nextdns.connection_status(self.profile_id)
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as err:
            raise UpdateFailed(err) from err
