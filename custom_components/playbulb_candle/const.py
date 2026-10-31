"""Constants for PLAYBULB Candle."""
from typing import Final

DOMAIN: Final = "playbulb_candle"
MANUFACTURER: Final = "MIPOW"
CHAR_COLOR: Final = "0000fffc-0000-1000-8000-00805f9b34fb"
CHAR_EFFECT: Final = "0000fffb-0000-1000-8000-00805f9b34fb"
CHAR_BATTERY: Final = "00002a19-0000-1000-8000-00805f9b34fb"
EFFECT_NONE: Final = 0xFF
DEFAULT_EFFECT_SPEED: Final = 50
EFFECTS: Final = {
    "Kein Effekt": 0xFF,
    "Blitz": 0,
    "Pulsieren": 1,
    "Regenbogen": 2,
    "Regenbogen (sanft)": 3,
    "Kerzenlicht": 4,
}
