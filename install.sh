#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HA_CONFIG:-/config}"
SOURCE="$SCRIPT_DIR/custom_components/playbulb_candle"
DEST="$CONFIG_DIR/custom_components/playbulb_candle"

if [[ ! -d "$SOURCE" ]]; then
  echo "Fehler: $SOURCE nicht gefunden. Bitte Paket zuerst vollständig entpacken." >&2
  exit 1
fi
mkdir -p "$CONFIG_DIR/custom_components"
mkdir -p "$DEST"
cp -R "$SOURCE"/. "$DEST"/
echo "PLAYBULB Candle installiert nach $DEST"
echo "Bitte Home Assistant neu starten."
