# PLAYBULB Candle für Home Assistant

Custom-Integration für MIPOW PLAYBULB Candle-Leuchten über Bluetooth LE. Verbindet sich über den Home-Assistant-Bluetooth-Stack (einschließlich Bluetooth-Proxy), fragt Zustand und optional den Batteriestand ab und stellt eine RGBW-Leuchte mit Effekten bereit.

## Installation über HACS (Custom Repository)

1. Dieses Repository in GitHub als Repository bereitstellen.
2. In HACS **Integrationen → ⋮ → Benutzerdefinierte Repositories** öffnen.
3. Repository-URL eintragen und als Kategorie **Integration** wählen, dann hinzufügen.
4. „PLAYBULB Candle“ installieren und Home Assistant neu starten.
5. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach PLAYBULB Candle suchen oder das Gerät per Bluetooth entdecken lassen.

## Manuelle Installation

Den Ordner `custom_components/playbulb_candle` in das Verzeichnis `config/custom_components/playbulb_candle` der Home-Assistant-Konfiguration kopieren. Home Assistant neu starten und die Integration über **Geräte & Dienste** hinzufügen.

### Samba

Öffne die Home-Assistant-Konfigurationsfreigabe (typischerweise `\homeassistant\config`), erstelle bei Bedarf `custom_components` und kopiere den Ordner `playbulb_candle` dorthin. Danach Home Assistant neu starten.

### SSH / Terminal

Entpacke das Paket zunächst in dein Arbeitsverzeichnis und führe das enthaltene Skript im Home-Assistant-Terminal aus:

```sh
unzip playbulb_candle.zip -d /tmp/playbulb_candle
cd /tmp/playbulb_candle
bash install.sh
```

Das Skript kopiert `custom_components/playbulb_candle` nach `/config/custom_components/playbulb_candle`. Falls dein Konfigurationsverzeichnis nicht `/config` ist, setze vorher `HA_CONFIG=/dein/pfad`.

## Hinweise

- Bluetooth muss für Home Assistant eingerichtet sein; kompatible Bluetooth-Proxies werden über den HA-Bluetooth-Stack unterstützt.
- Bei der Auswahl bzw. Bestätigung des Geräts wird die MAC-Adresse angezeigt; die Batterie-Entität zeigt „unbekannt“, wenn die Batterie-Characteristic nicht lesbar ist.
- In der Geräteübersicht werden Hersteller (MIPOW), Modell sowie – falls vom Gerät lesbar – Firmware-Version, Hardware-Version und Seriennummer angezeigt.
- Der Regler **Effektgeschwindigkeit** (1–100) steuert das Tempo von Effekten; auf einen laufenden Effekt wirkt er sofort. Der Wert wird bei laufendem Effekt vom Gerät gelesen und bleibt über Neustarts erhalten.
- Beim Einschalten ohne Farbangabe wird die zuletzt verwendete Farbe wiederhergestellt.
- Die Integration pollt im 60-Sekunden-Intervall.

## Lizenz

Diese Integration steht unter der MIT-Lizenz (siehe [LICENSE](LICENSE)).
