# Changelog

## Unveröffentlicht

### Hinzugefügt
- Integrations-Icon (`brand/icon.png` 256×256, `brand/icon@2x.png` 512×512) aus einem Produktfoto der Kerze erstellt.

### Behoben
- Abbruchmeldungen im Einrichtungsdialog (`no_devices_found`, `already_configured`) werden wieder korrekt übersetzt angezeigt.
- Regler „Effektgeschwindigkeit“ aktualisiert seinen Zustand sofort statt erst beim nächsten Poll.
- Effektgeschwindigkeit wird bei laufendem Effekt vom Gerät gelesen und über HA-Neustarts wiederhergestellt.
- Einschalten ohne Farbangabe stellt die zuletzt verwendete Farbe wieder her statt immer Weiß.
- Fehler beim Laden der Number-Plattform behoben: falscher Import `NumberDisplayMode` durch `NumberMode` ersetzt. Das war auch die Ursache der Warnung „Detected blocking call to import_module“. Die Plattformen werden zusätzlich vorab geladen.
