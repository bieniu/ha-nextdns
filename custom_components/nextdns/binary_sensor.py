"""Support for the NextDNS service."""
from __future__ import annotations

from dataclasses import dataclass

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


@dataclass
class NextDnsBinarySensorRequiredKeysMixin:
    """Mixin for required keys."""

    entity_class: type[NextDnsBinarySensor]


@dataclass
class NextDnsBinarySensorEntityDescription(
    BinarySensorEntityDescription, NextDnsBinarySensorRequiredKeysMixin
):
    """NextDNS sensor entity description."""


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
        self.entity_description = description

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data.connected
        self.async_write_ha_state()


class NextDnsProfileBinarySensor(NextDnsBinarySensor):
    """Define an NextDNS binary sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = (
            self.coordinator.data.profile_id == self.coordinator.profile_id
        )
        self.async_write_ha_state()


SENSORS = (
    NextDnsBinarySensorEntityDescription(
        key="this_device_nextdns_connection_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        name="This Device NextDNS Connection Status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_class=NextDnsBinarySensor,
    ),
    NextDnsBinarySensorEntityDescription(
        key="this_device_profile_connection_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        name="This Device Profile Connection Status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_class=NextDnsProfileBinarySensor,
    ),
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
    for description in SENSORS:
        sensors.append(description.entity_class(coordinator, description))

    async_add_entities(sensors, True)
