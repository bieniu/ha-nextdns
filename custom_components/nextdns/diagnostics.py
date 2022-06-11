"""Diagnostics support for NextDNS."""
from __future__ import annotations

from dataclasses import asdict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import NextDnsDataUpdateCoordinator
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator: NextDnsDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    diagnostics_data = {
        "config_entry_data": dict(config_entry.data),
        "coordinator_data": asdict(coordinator.data),
    }

    return diagnostics_data
