"""Config flow for PLAYBULB Candle."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import callback

from .const import DOMAIN


def _is_playbulb(info: BluetoothServiceInfoBleak) -> bool:
    name = (info.name or info.device.name or "").lower()
    return name.startswith("playbulb") or "0000ff0d-0000-1000-8000-00805f9b34fb" in {
        uuid.lower() for uuid in info.advertisement.service_uuids
    }


class PlaybulbConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle discovery and user configuration."""

    VERSION = 1

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        """Handle a Bluetooth discovery and confirm setup."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": discovery_info.name or "PLAYBULB Candle"}
        self._discovery_info = discovery_info
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input: dict[str, Any] | None = None):
        """Confirm a discovered device."""
        if not hasattr(self, "_discovery_info"):
            return self.async_abort(reason="no_devices_found")
        if user_input is not None:
            info = self._discovery_info
            return self.async_create_entry(
                title=info.name or "PLAYBULB Candle",
                data={"address": info.address, "name": info.name or "PLAYBULB Candle"},
            )
        return self.async_show_form(step_id="bluetooth_confirm", description_placeholders={"name": self.context["title_placeholders"]["name"]})

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Allow selection from discovered, not-yet-configured devices."""
        if user_input is not None:
            address = user_input["address"]
            info = next((item for item in bluetooth.async_discovered_service_info(self.hass, connectable=True)
                         if item.address == address), None)
            if info is None:
                return self.async_abort(reason="no_devices_found")
            return await self.async_step_bluetooth(info)

        devices: dict[str, str] = {}
        for info in bluetooth.async_discovered_service_info(self.hass, connectable=True):
            if not _is_playbulb(info) or self._async_current_entries():
                # The configured-address check below is authoritative; don't exclude all entries.
                if not _is_playbulb(info):
                    continue
            if any(entry.unique_id == info.address for entry in self._async_current_entries()):
                continue
            devices[info.address] = f"{info.name or 'PLAYBULB Candle'} ({info.address})"
        if not devices:
            return self.async_abort(reason="no_devices_found")
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required("address"): vol.In(devices)}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return config_entries.OptionsFlow(config_entry)
