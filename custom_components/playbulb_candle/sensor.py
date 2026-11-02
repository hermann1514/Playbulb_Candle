"""Battery sensor for PLAYBULB Candle."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PlaybulbCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: PlaybulbCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PlaybulbBattery(coordinator, entry)])


class PlaybulbBattery(CoordinatorEntity[PlaybulbCoordinator], SensorEntity):
    """Battery level; unknown while the characteristic is not readable."""

    _attr_has_entity_name = True
    _attr_translation_key = "battery"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(self, coordinator: PlaybulbCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_battery"

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info()

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("battery")
