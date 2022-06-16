"""Support for the NextDNS service."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NextDnsConnectionUpdateCoordinator
from .const import ATTR_CONNECTION, DOMAIN

PARALLEL_UPDATES = 1


DEVICE_CONNECTION_STATUS_SENSORS = BinarySensorEntityDescription(
    key="this_device_status",
    entity_category=EntityCategory.DIAGNOSTIC,
    name="{profile_name} This Device Status",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a NextDNS entities from a config_entry."""
    coordinator: NextDnsConnectionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        ATTR_CONNECTION
    ]

    sensors: list[NextDnsBinarySensor] = []
    sensors.append(NextDnsBinarySensor(coordinator, DEVICE_CONNECTION_STATUS_SENSORS))

    async_add_entities(sensors)


class NextDnsBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Define an NextDNS binary sensor."""

    coordinator: NextDnsConnectionUpdateCoordinator

    def __init__(
        self,
        coordinator: NextDnsConnectionUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.profile_id}-{description.key}"
        self._attr_name = description.name.format(profile_name=coordinator.profile_name)
        self._attr_is_on = coordinator.data.connected
        self.entity_description = description

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data.connected
        self.async_write_ha_state()
