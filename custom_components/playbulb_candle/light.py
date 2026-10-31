"""Light platform for PLAYBULB Candle."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity, LightEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EFFECT_NONE, EFFECTS, MANUFACTURER
from .coordinator import PlaybulbCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([PlaybulbLight(hass.data[DOMAIN][entry.entry_id], entry)])


class PlaybulbLight(CoordinatorEntity[PlaybulbCoordinator], LightEntity):
    """PLAYBULB Candle RGBW light."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.RGBW}
    _attr_color_mode = ColorMode.RGBW
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = list(EFFECTS)

    def __init__(self, coordinator: PlaybulbCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = entry.unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            connections={(CONNECTION_BLUETOOTH, coordinator.address)},
            name=coordinator.name,
            manufacturer=MANUFACTURER,
            model="PLAYBULB Candle",
        )
        self._attr_is_on = False

    @property
    def _effect_mode(self) -> int:
        return (self.coordinator.data or {}).get("effect", EFFECT_NONE)

    @property
    def is_on(self) -> bool:
        color = (self.coordinator.data or {}).get("color", (0, 0, 0, 0))
        return any(color) or self._effect_mode != EFFECT_NONE

    @property
    def rgbw_color(self) -> tuple[int, int, int, int]:
        data = self.coordinator.data or {}
        color = data.get("color", (255, 255, 255, 0))
        if not any(color) and self._effect_mode != EFFECT_NONE:
            effect_color = data.get("effect_color")
            if effect_color and any(effect_color):
                return effect_color
        return color

    @property
    def brightness(self) -> int:
        return max(self.rgbw_color)

    @property
    def effect(self) -> str | None:
        mode = self._effect_mode
        return next((name for name, value in EFFECTS.items() if value == mode), "Kein Effekt")

    async def async_turn_on(self, **kwargs: Any) -> None:
        color = tuple(kwargs.get("rgbw_color", self.rgbw_color))
        brightness = kwargs.get("brightness")
        if not any(color):
            color = (255, 255, 255, 0)
        if brightness is not None:
            current = max(color) or 255
            factor = brightness / current
            color = tuple(round(component * factor) for component in color)

        current_mode = self._effect_mode
        effect_name = kwargs.get("effect")
        if effect_name in EFFECTS:
            mode = EFFECTS[effect_name]
        else:
            # No effect requested: keep a running effect (e.g. when only the
            # brightness or color changes) instead of silently stopping it.
            mode = current_mode

        if mode != EFFECT_NONE:
            await self.coordinator.async_write_effect(mode, color)
        else:
            if current_mode != EFFECT_NONE:
                await self.coordinator.async_write_effect(EFFECT_NONE, color)
            await self.coordinator.async_write_color(color)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self._effect_mode != EFFECT_NONE:
            await self.coordinator.async_write_effect(EFFECT_NONE, (0, 0, 0, 0))
        await self.coordinator.async_write_color((0, 0, 0, 0))
        await self.coordinator.async_request_refresh()
