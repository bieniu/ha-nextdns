"""Support for the NextDNS service."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NextDnsAnalyticsDataUpdateCoordinator
from .const import DOMAIN

PARALLEL_UPDATES = 1

CLEAR_LOGS_BUTTON = ButtonEntityDescription(
    key="clear_logs",
    name="{profile_name} Clear Logs",
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add aNextDNS entities from a config_entry."""
    coordinator: NextDnsAnalyticsDataUpdateCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]["analytics"]

    buttons: list[NextDnsButton] = []
    buttons.append(NextDnsButton(coordinator, CLEAR_LOGS_BUTTON))

    async_add_entities(buttons, False)


class NextDnsButton(
    CoordinatorEntity[NextDnsAnalyticsDataUpdateCoordinator], ButtonEntity
):
    """Define an NextDNS button."""

    def __init__(
        self,
        coordinator: NextDnsAnalyticsDataUpdateCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.profile_id}-{description.key}"
        self._attr_name = description.name.format(profile_name=coordinator.profile_name)
        self.entity_description = description

    async def async_press(self) -> None:
        """Trigger cleaning logs."""
        await self.coordinator.nextdns.clear_logs(self.coordinator.profile_id)
