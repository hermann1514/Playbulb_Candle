# Changelog

## Unveröffentlicht

### Behoben
- Abbruchmeldungen im Einrichtungsdialog (`no_devices_found`, `already_configured`) werden wieder korrekt übersetzt angezeigt.
- Regler „Effektgeschwindigkeit“ aktualisiert seinen Zustand sofort statt erst beim nächsten Poll.
- Effektgeschwindigkeit wird bei laufendem Effekt vom Gerät gelesen und über HA-Neustarts wiederhergestellt.
- Einschalten ohne Farbangabe stellt die zuletzt verwendete Farbe wieder her statt immer Weiß.
- Warnung „Detected blocking call to import_module“ beim Einrichten behoben: Die Plattformen werden jetzt vorab geladen.
