"""Support for the NextDNS service."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NextDnsAnalyticsUpdateCoordinator
from .const import DOMAIN

PARALLEL_UPDATES = 1


@dataclass
class NextDnsSensorRequiredKeysMixin:
    """Class for NextDNS entity required keys."""

    parent_key: str


@dataclass
class NextDnsSensorEntityDescription(
    SensorEntityDescription, NextDnsSensorRequiredKeysMixin
):
    """NextDNS sensor entity description."""


SENSORS = (
    NextDnsSensorEntityDescription(
        key="all_queries",
        parent_key="status",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:dns",
        name="{profile_name} DNS Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="blocked_queries",
        parent_key="status",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:dns",
        name="{profile_name} DNS Queries Blocked",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="blocked_queries_ratio",
        parent_key="status",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:dns",
        name="{profile_name} DNS Queries Blocked Ratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="doh_queries",
        parent_key="protocols",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:dns",
        name="{profile_name} DNS-over-HTTPS Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="dot_queries",
        parent_key="protocols",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:dns",
        name="{profile_name} DNS-over-TLS Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="udp_queries",
        icon="mdi:dns",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        name="{profile_name} UDP Queries",
        native_unit_of_measurement="queries",
        parent_key="protocols",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="doh_queries_ratio",
        parent_key="protocols",
        icon="mdi:dns",
        entity_category=EntityCategory.DIAGNOSTIC,
        name="{profile_name} DNS-over-HTTPS Queries Ratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="dot_queries_ratio",
        parent_key="protocols",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:dns",
        name="{profile_name} DNS-over-TLS Queries Ratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="udp_queries_ratio",
        parent_key="protocols",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:dns",
        name="{profile_name} UDP Queries Ratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="encrypted_queries",
        parent_key="encrypted",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:lock",
        name="{profile_name} Encrypted Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="unencrypted_queries",
        parent_key="encrypted",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:lock-open",
        name="{profile_name} Unncrypted Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="encrypted_queries_ratio",
        parent_key="encrypted",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:lock",
        name="{profile_name} Encrypted Queries Ratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="ipv4_queries",
        parent_key="ip_versions",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:ip",
        name="{profile_name} IPv4 Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="ipv6_queries",
        parent_key="ip_versions",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:ip",
        name="{profile_name} IPv6 Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="ipv6_queries_ratio",
        parent_key="ip_versions",
        name="{profile_name} IPv6 Queries Ratio",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:ip",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NextDnsSensorEntityDescription(
        key="validated_queries",
        parent_key="dnssec",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:lock-check",
        name="{profile_name} DNSSEC Validated Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="not_validated_queries",
        parent_key="dnssec",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:lock-alert",
        name="{profile_name} DNSSEC Not Validated Queries",
        native_unit_of_measurement="queries",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NextDnsSensorEntityDescription(
        key="validated_queries_ratio",
        parent_key="dnssec",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:lock-check",
        name="{profile_name} DNSSEC Validated Queries Ratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a NextDNS entities from a config_entry."""
    coordinator: NextDnsAnalyticsUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "analytics"
    ]

    sensors = []
    for description in SENSORS:
        sensors.append(NextDnsSensor(coordinator, description))

    async_add_entities(sensors)


class NextDnsSensor(CoordinatorEntity, SensorEntity):
    """Define an NextDNS sensor."""

    coordinator: NextDnsAnalyticsUpdateCoordinator

    def __init__(
        self,
        coordinator: NextDnsAnalyticsUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.profile_id}-{description.key}"
        self._attr_name = description.name.format(profile_name=coordinator.profile_name)
        sensor_data = getattr(coordinator.data, description.parent_key)
        self._attr_native_value = getattr(sensor_data, description.key)
        self.entity_description = description

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        sensor_data = getattr(self.coordinator.data, self.entity_description.parent_key)
        self._attr_native_value = getattr(sensor_data, self.entity_description.key)
        self.async_write_ha_state()
