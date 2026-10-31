"""Optional battery sensor for PLAYBULB Candle."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PlaybulbCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: PlaybulbCoordinator = hass.data[DOMAIN][entry.entry_id]
    if (coordinator.data or {}).get("battery") is not None:
        async_add_entities([PlaybulbBattery(coordinator, entry)])


class PlaybulbBattery(CoordinatorEntity[PlaybulbCoordinator], SensorEntity):
    """Battery level, when the characteristic is readable."""

    _attr_has_entity_name = True
    _attr_name = "Batterie"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(self, coordinator: PlaybulbCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_battery"
        self._attr_device_info = self._device_info_from_light(coordinator, entry)

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("battery")


def _device_info_from_light(coordinator: PlaybulbCoordinator, entry: ConfigEntry):
    from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
    from .const import MANUFACTURER
    return DeviceInfo(
        identifiers={(DOMAIN, entry.unique_id)},
        connections={(CONNECTION_BLUETOOTH, coordinator.address)},
        name=coordinator.name,
        manufacturer=MANUFACTURER,
        model="PLAYBULB Candle",
    )
