"""Effect speed number entity for PLAYBULB Candle."""
from __future__ import annotations

from homeassistant.components.number import NumberDisplayMode, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EFFECT_NONE, EFFECT_SPEED_MAX, EFFECT_SPEED_MIN
from .coordinator import PlaybulbCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: PlaybulbCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PlaybulbEffectSpeed(coordinator, entry)])


class PlaybulbEffectSpeed(CoordinatorEntity[PlaybulbCoordinator], NumberEntity):
    """Slider controlling the speed of running light effects."""

    _attr_has_entity_name = True
    _attr_translation_key = "effect_speed"
    _attr_native_min_value = EFFECT_SPEED_MIN
    _attr_native_max_value = EFFECT_SPEED_MAX
    _attr_native_step = 1
    _attr_mode = NumberDisplayMode.SLIDER

    def __init__(self, coordinator: PlaybulbCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_effect_speed"

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info()

    @property
    def native_value(self) -> float:
        return self.coordinator.effect_speed

    async def async_set_native_value(self, value: float) -> None:
        speed = int(value)
        self.coordinator.effect_speed = speed
        mode = (self.coordinator.data or {}).get("effect", EFFECT_NONE)
        if mode != EFFECT_NONE:
            # A running effect is restarted with the new speed so the change
            # takes effect on the candle immediately.
            await self.coordinator.async_write_effect(mode, speed=speed)