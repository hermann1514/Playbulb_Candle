"""Bluetooth connection and polling coordinator."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from bleak import BleakClient
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CHAR_BATTERY, CHAR_COLOR, CHAR_EFFECT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PlaybulbCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Maintain one BLE connection and read bulb state every minute."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{entry.entry_id}", update_interval=__import__("datetime").timedelta(seconds=60))
        self.hass = hass
        self.address = entry.data["address"]
        self.name = entry.data.get("name", "PLAYBULB Candle")
        self.client: BleakClient | None = None
        self._lock = asyncio.Lock()

    async def _ensure_connected(self) -> BleakClient:
        if self.client is not None and self.client.is_connected:
            return self.client
        device = bluetooth.async_ble_device_from_address(self.hass, self.address, connectable=True)
        if device is None:
            raise UpdateFailed(f"Bluetooth-Gerät {self.address} ist nicht erreichbar")
        service_info = bluetooth.async_discovered_service_info(self.hass, connectable=True)
        name = next((info.name for info in service_info if info.address == self.address), self.name)
        try:
            self.client = await establish_connection(
                BleakClientWithServiceCache, device, name,
                disconnected_callback=self._handle_disconnect,
            )
        except Exception as err:
            raise UpdateFailed(f"Verbindung zur PLAYBULB fehlgeschlagen: {err}") from err
        return self.client

    def _handle_disconnect(self, _client: BleakClient) -> None:
        self.client = None
        self.async_set_updated_data(self.data or {})

    async def _async_update_data(self) -> dict[str, Any]:
        async with self._lock:
            client = await self._ensure_connected()
            try:
                color = bytes(await client.read_gatt_char(CHAR_COLOR))
                if len(color) != 4:
                    raise ValueError(f"Ungültige Farbdaten ({len(color)} Bytes)")
                try:
                    effect_data = bytes(await client.read_gatt_char(CHAR_EFFECT))
                    effect = effect_data[4] if len(effect_data) >= 5 else 0xFF
                except Exception:
                    effect = 0xFF
                battery = None
                try:
                    battery_data = bytes(await client.read_gatt_char(CHAR_BATTERY))
                    if battery_data:
                        battery = battery_data[0]
                except Exception:
                    pass
                return {"color": (color[1], color[2], color[3], color[0]), "effect": effect, "battery": battery}
            except Exception as err:
                await self._disconnect_locked()
                raise UpdateFailed(f"Lesen der PLAYBULB fehlgeschlagen: {err}") from err

    async def async_write_color(self, rgbw: tuple[int, int, int, int]) -> None:
        async with self._lock:
            client = await self._ensure_connected()
            try:
                characteristic = client.services.get_characteristic(CHAR_COLOR)
                if characteristic is None:
                    raise ValueError(f"Farb-Characteristic {CHAR_COLOR} nicht gefunden")
                properties = characteristic.properties
                if "write-without-response" in properties:
                    response = False
                elif "write" in properties:
                    response = True
                else:
                    raise ValueError(
                        f"Farb-Characteristic {CHAR_COLOR} unterstützt kein Schreiben "
                        f"(Properties: {properties})"
                    )
                r, g, b, w = (max(0, min(255, int(value))) for value in rgbw)
                await client.write_gatt_char(CHAR_COLOR, bytes((w, r, g, b)), response=response)
            except Exception:
                await self._disconnect_locked()
                raise

    async def async_write_effect(self, mode: int, speed: int = 50) -> None:
        async with self._lock:
            client = await self._ensure_connected()
            current = (self.data or {}).get("color", (255, 255, 255, 0))
            r, g, b, w = current
            try:
                payload = bytes((w, r, g, b, mode & 0xFF, 0, max(0, min(255, speed)), 0))
                await client.write_gatt_char(CHAR_EFFECT, payload, response=True)
            except Exception:
                await self._disconnect_locked()
                raise

    async def async_disconnect(self) -> None:
        async with self._lock:
            await self._disconnect_locked()

    async def _disconnect_locked(self) -> None:
        client, self.client = self.client, None
        if client is not None and client.is_connected:
            try:
                await client.disconnect()
            except Exception:
                _LOGGER.debug("Disconnect PLAYBULB fehlgeschlagen", exc_info=True)
