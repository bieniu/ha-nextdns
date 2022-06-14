"""Diagnostics support for NextDNS."""
from __future__ import annotations

from dataclasses import asdict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import NextDnsAnalyticsDataUpdateCoordinator, NextDnsStatusDataUpdateCoordinator
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    analytics_coordinator: NextDnsAnalyticsDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["analytics"]
    status_coordinator: NextDnsStatusDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["status"]

    diagnostics_data = {
        "config_entry_data": dict(config_entry.data),
        "analytics_coordinator_data": asdict(analytics_coordinator.data),
        "status_coordinator_data": asdict(status_coordinator.data),
    }

    return diagnostics_data
