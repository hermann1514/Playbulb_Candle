"""Constants for PLAYBULB Candle."""
from typing import Final

DOMAIN: Final = "playbulb_candle"
MANUFACTURER: Final = "MIPOW"
CHAR_COLOR: Final = "0000fffc-0000-1000-8000-00805f9b34fb"
CHAR_EFFECT: Final = "0000fffb-0000-1000-8000-00805f9b34fb"
CHAR_BATTERY: Final = "00002a19-0000-1000-8000-00805f9b34fb"
# Standard Bluetooth SIG Device Information Service (für Geräteübersicht)
CHAR_MODEL: Final = "00002a24-0000-1000-8000-00805f9b34fb"
CHAR_SERIAL: Final = "00002a25-0000-1000-8000-00805f9b34fb"
CHAR_FIRMWARE: Final = "00002a26-0000-1000-8000-00805f9b34fb"
CHAR_HARDWARE: Final = "00002a27-0000-1000-8000-00805f9b34fb"
EFFECT_NONE: Final = 0xFF
DEFAULT_EFFECT_SPEED: Final = 50
EFFECT_SPEED_MIN: Final = 1
EFFECT_SPEED_MAX: Final = 100
EFFECTS: Final = {
    "Kein Effekt": 0xFF,
    "Blitz": 0,
    "Pulsieren": 1,
    "Regenbogen": 2,
    "Regenbogen (sanft)": 3,
    "Kerzenlicht": 4,
}
