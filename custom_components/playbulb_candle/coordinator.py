"""Bluetooth connection and polling coordinator."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from bleak import BleakClient
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CHAR_BATTERY,
    CHAR_COLOR,
    CHAR_EFFECT,
    CHAR_FIRMWARE,
    CHAR_HARDWARE,
    CHAR_MODEL,
    CHAR_SERIAL,
    DEFAULT_EFFECT_SPEED,
    DOMAIN,
    EFFECT_NONE,
    EFFECT_SPEED_MAX,
    EFFECT_SPEED_MIN,
    MANUFACTURER,
)

_LOGGER = logging.getLogger(__name__)


class PlaybulbCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Maintain one BLE connection and read bulb state every minute."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=60),
        )
        self.hass = hass
        self.address = entry.data["address"]
        self.name = entry.data.get("name", "PLAYBULB Candle")
        self.client: BleakClient | None = None
        self._lock = asyncio.Lock()
        self.effect_speed: int = DEFAULT_EFFECT_SPEED
        # Last non-black color, restored when the light is turned on without a color
        self.last_color: tuple[int, int, int, int] = (255, 255, 255, 0)
        self.device_meta: dict[str, Any] = {}
        self._meta_read = False

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

    async def _read_device_meta(self, client: BleakClient) -> None:
        """Read the standard Device Information characteristics once per connection cycle."""
        for key, uuid in (
            ("model", CHAR_MODEL),
            ("serial_number", CHAR_SERIAL),
            ("sw_version", CHAR_FIRMWARE),
            ("hw_version", CHAR_HARDWARE),
        ):
            try:
                raw = bytes(await client.read_gatt_char(uuid))
            except Exception:
                continue
            value = raw.decode("utf-8", "replace").strip("\x00 ")
            if value:
                self.device_meta[key] = value
        self._meta_read = True

    async def _async_update_data(self) -> dict[str, Any]:
        async with self._lock:
            client = await self._ensure_connected()
            if not self._meta_read:
                await self._read_device_meta(client)
            try:
                color = bytes(await client.read_gatt_char(CHAR_COLOR))
                if len(color) != 4:
                    raise ValueError(f"Ungültige Farbdaten ({len(color)} Bytes)")
                effect_color = None
                try:
                    effect_data = bytes(await client.read_gatt_char(CHAR_EFFECT))
                    effect = effect_data[4] if len(effect_data) >= 5 else 0xFF
                    if len(effect_data) >= 4:
                        effect_color = (effect_data[1], effect_data[2], effect_data[3], effect_data[0])
                    if effect != EFFECT_NONE and len(effect_data) >= 7 and effect_data[6]:
                        self.effect_speed = max(
                            EFFECT_SPEED_MIN, min(EFFECT_SPEED_MAX, effect_data[6])
                        )
                except Exception:
                    effect = 0xFF
                battery = None
                try:
                    battery_data = bytes(await client.read_gatt_char(CHAR_BATTERY))
                    if battery_data:
                        battery = battery_data[0]
                except Exception:
                    pass
                rgbw = (color[1], color[2], color[3], color[0])
                if any(rgbw):
                    self.last_color = rgbw
                elif effect_color and any(effect_color):
                    self.last_color = effect_color
                return {
                    "color": rgbw,
                    "effect": effect,
                    "effect_color": effect_color,
                    "battery": battery,
                }
            except Exception as err:
                await self._disconnect_locked()
                raise UpdateFailed(f"Lesen der PLAYBULB fehlgeschlagen: {err}") from err

    @staticmethod
    async def _write_char(client: BleakClient, uuid: str, payload: bytes) -> None:
        """Write a characteristic, preferring write-without-response."""
        characteristic = client.services.get_characteristic(uuid)
        if characteristic is None:
            raise ValueError(f"Characteristic {uuid} nicht gefunden")
        properties = characteristic.properties
        if "write-without-response" in properties:
            response = False
        elif "write" in properties:
            response = True
        else:
            raise ValueError(
                f"Characteristic {uuid} unterstützt kein Schreiben (Properties: {properties})"
            )
        await client.write_gatt_char(uuid, payload, response=response)

    async def async_write_color(self, rgbw: tuple[int, int, int, int]) -> None:
        async with self._lock:
            client = await self._ensure_connected()
            try:
                r, g, b, w = (max(0, min(255, int(value))) for value in rgbw)
                await self._write_char(client, CHAR_COLOR, bytes((w, r, g, b)))
                if any((r, g, b, w)):
                    self.last_color = (r, g, b, w)
            except Exception:
                await self._disconnect_locked()
                raise

    async def async_write_effect(
        self,
        mode: int,
        color: tuple[int, int, int, int] | None = None,
        speed: int | None = None,
    ) -> None:
        async with self._lock:
            client = await self._ensure_connected()
            if speed is None:
                speed = self.effect_speed
            if color is None:
                color = (self.data or {}).get("color", (255, 255, 255, 0))
            r, g, b, w = (max(0, min(255, int(value))) for value in color)
            try:
                payload = bytes((w, r, g, b, mode & 0xFF, 0, max(0, min(255, int(speed))), 0))
                await self._write_char(client, CHAR_EFFECT, payload)
            except Exception:
                await self._disconnect_locked()
                raise

    def device_info(self) -> DeviceInfo:
        """Build the device registry entry, enriched with BLE device metadata."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.address)},
            connections={(CONNECTION_BLUETOOTH, self.address)},
            name=self.name,
            manufacturer=MANUFACTURER,
            model=self.device_meta.get("model") or "PLAYBULB Candle",
            sw_version=self.device_meta.get("sw_version"),
            hw_version=self.device_meta.get("hw_version"),
            serial_number=self.device_meta.get("serial_number"),
        )

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
