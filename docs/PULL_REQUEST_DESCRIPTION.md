# Suggested title

Add ESP32-C3 support, runtime clock settings, and ESPHome fixes

# Suggested description

The clock currently needs firmware edits to change its time zone or Home Assistant temperature source, and the original pin assignments target the classic ESP32. This change adds a shared ESP32-C3 SuperMini configuration and saved device controls, together with ESPHome configuration and display fixes.

## Changes

- Add a C3 SuperMini entry point using GPIO6/7/10 and native USB logging, while sharing the existing clock implementation.
- Add saved **Time Zone**, **Temperature Entity**, and **Weekday Language** controls. Zone and language changes apply immediately; an **Apply Sensor (Restart)** button saves settings and restarts to bind the new sensor subscription.
- Include the four-digit year in the date. Keep German weekdays as the default and offer English `SU MO TU WE TH FR SA`.
- Correct captive portal placement, use `!secret` credentials, send runtime brightness commands consistently, disable competing driver scrolling, and handle invalid temperature readings.
- Document setup, electrical requirements, migration, and validation; add display and runtime settings test scripts.

The initial local settings remain Europe/Berlin, German weekday abbreviations, and the original temperature sensor ID. The original author's clock design, fonts, icons, and attribution are retained.

## Validation

- Both board configurations validate with ESPHome **2026.9.1**.
- The full C3 build succeeds with ESP-IDF **5.5.5** and the Arduino framework: 1,037,494 bytes of flash and 109,718 bytes of reported RAM.
- The display simulation passes schedule, brightness, power, icons, date/year, both weekday languages, invalid-data, and text-animation checks.
- Runtime settings tests pass **6,343 timezone/DST cases** against Python `zoneinfo`, plus entity binding and save/restart scenarios.

The latest classic ESP32 configuration has been validated but has not had a full rebuild after these feature additions. Physical board/display operation, settings persistence, and Home Assistant reconnection still need hardware verification. Build memory figures do not measure runtime heap.

## Installation impact

Requires **ESPHome 2026.9.1+** and `clock_settings.h` beside the device YAML. Existing users keep their secrets file, match the `!secret` names to their entries, and install one firmware update. Later settings changes use the device controls.

Details and test limits are documented in `docs/FORK_CHANGES.md` and `ESPHOME_VALIDATION.md`.
