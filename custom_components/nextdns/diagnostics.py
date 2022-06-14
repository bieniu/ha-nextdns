"""Diagnostics support for NextDNS."""
from __future__ import annotations

from dataclasses import asdict

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from . import NextDnsAnalyticsUpdateCoordinator, NextDnsStatusUpdateCoordinator
from .const import ATTR_ANALYTICS, DOMAIN

TO_REDACT = {CONF_API_KEY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    analytics_coordinator: NextDnsAnalyticsUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][ATTR_ANALYTICS]
    status_coordinator: NextDnsStatusUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["status"]

    diagnostics_data = {
        "config_entry_data": async_redact_data(config_entry.data, TO_REDACT),
        "analytics_coordinator_data": asdict(analytics_coordinator.data),
        "status_coordinator_data": asdict(status_coordinator.data),
    }

    return diagnostics_data
