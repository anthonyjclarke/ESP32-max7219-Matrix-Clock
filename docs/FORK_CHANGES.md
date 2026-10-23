# Changes since the original fork

Prepared on 23 October 2026 for a proposed contribution to [OlLiLe18/ESP32-max7219-Matrix-Clock](https://github.com/OlLiLe18/ESP32-max7219-Matrix-Clock).

This fork adds ESPHome compatibility fixes, an alternative ESP32-C3 SuperMini configuration, and saved clock settings. The original author supplied the 96×8 clock, icons, fonts, Home Assistant integration, night mode, and text animations; those form the foundation of this work.

## Comparison baseline

The fork and original repository share commit [`15111dd`](https://github.com/OlLiLe18/ESP32-max7219-Matrix-Clock/commit/15111dd2b66a916ff17b6d82e617d9cfed14f02f), “Revise donation section in README.md”. This document describes changes from that common ancestor to the current working files, including work that has not yet been committed.

The original repository has also developed independently. At preparation time, its `main` branch was at `95e8465`, with ten commits after the common ancestor. Those updates add English documentation alongside German content and relocate the clock image into `images/`. The firmware changes described below are still additions relative to that upstream version. The historical README translation overlaps with upstream's newer documentation and needs reconciliation before an upstream PR.

## ESPHome compatibility and display fixes

| Area | Change and resulting behaviour |
| ---- | ------------------------------ |
| Captive portal | Move `captive_portal:` out of `wifi.ap` to a top-level component so the configuration validates. |
| Credentials | Replace inline placeholders with `!secret` references. Supply a flat `secrets.example.yaml` mapping, with instructions to generate a valid API encryption key and reuse existing secret names. |
| Runtime brightness | Use the MAX7219 driver's runtime `intensity()` method to send brightness changes to the chips. Apply power and day/night brightness together in the display lambda, avoiding conflicting callbacks and cache state. |
| Text animation | Set `scroll_enable: false` so the driver's automatic scrolling does not compete with the existing custom animations. |
| Missing temperature | Check that the imported value is finite. Missing, unavailable, or nonnumeric readings display `--.-°`. |

## Alternative ESP32-C3 SuperMini

[`max7219-esp32c3-supermini.yaml`](../max7219-esp32c3-supermini.yaml) includes the classic ESP32 configuration as an ESPHome package, then overrides its board, device name, display pins, native USB logging, and fallback hotspot name. Both boards use the same rendering code and controls.

| Signal | Classic ESP32 | ESP32-C3 SuperMini |
| ------ | ------------- | ----------------- |
| CLK | GPIO26 | GPIO6 |
| DIN / MOSI | GPIO27 | GPIO7 |
| CS / LOAD | GPIO25 | GPIO10 |

The C3 configuration uses the generic `esp32-c3-devkitm-1` target with `variant: esp32c3`, the Arduino framework, and native `USB_SERIAL_JTAG` logging. It assumes a typical 4 MB SuperMini. Documentation covers the regulated 5 V display supply, shared ground, signal-level buffering, and USB boot procedure. The display remains a 12-chip, 96×8 chain.

## Saved settings available after installation

These controls appear in Home Assistant and the clock's web interface:

| Control | Behaviour |
| ------- | --------- |
| **Time Zone** | Choose one of 19 supported zones. The clock, date, and night schedule use the selected zone immediately, including daylight-saving rules where applicable. |
| **Temperature Entity** | Save the full ID of a numeric Home Assistant temperature sensor, such as `sensor.outdoor_temperature`. |
| **Apply Sensor (Restart)** | Validate the entity name, flush pending settings, and restart to create the Home Assistant subscription for that sensor. A failed save or invalid name cancels the restart. |
| **Weekday Language** | Choose German, the default, or English. The date reads the setting on each display frame. |

![ESP32-C3 SuperMini Web UI with saved runtime settings](./images/esphome-web-ui.png)

*Screenshot supplied during fork development, showing the runtime controls with `Australia/Sydney` and English weekdays selected.*

[`clock_settings.h`](../clock_settings.h) supplies the timezone rules and entity-name validation. The sensor subscription uses an owned string bound after text settings restore and before the Home Assistant sensor starts. Editing the temperature field leaves the current source active until the restart is applied.

The controls restore after a normal restart. Flash writes are normally batched, so allow approximately a minute before removing power after changing the zone or language. The apply button explicitly flushes pending preferences.

Initial defaults remain `Europe/Berlin`, German weekdays, and `sensor.aussenthermometer_temperature`. The zone and entity defaults can also be set through `default_timezone` and `default_temperature_entity` substitutions before the first installation. Saved device values take precedence on subsequent boots.

## Date display

The numeric date now includes the year as `DD.MM.YYYY`. Weekdays are listed Sunday through Saturday:

| Language | Abbreviations | Example |
| -------- | ------------- | ------- |
| German, default | `SO MO DI MI DO FR SA` | `SO 23.08.2026` |
| English | `SU MO TU WE TH FR SA` | `SU 23.08.2026` |

The date still appears at seconds `:50`–`:55`, inclusive. Font metrics give a maximum width of 67 pixels for the tested date strings in either language, fitting from X=4 before the calendar icon at X=87.

## Documentation and verification tools

- English README and configuration comments, with credit and the original author's donation link.
- Installation instructions for both boards, file locations in Home Assistant, existing secret-name matching, runtime controls, and OTA updates.
- [`ESPHOME_VALIDATION.md`](../ESPHOME_VALIDATION.md), recording build versions, fixes, software checks, and remaining physical checks.
- [`scripts/check_display_logic.py`](../scripts/check_display_logic.py), which runs the actual display lambda in a host simulation.
- [`scripts/check_runtime_settings.py`](../scripts/check_runtime_settings.py), which exercises the settings helper and startup/apply lambdas with ESPHome's actual timezone converter.

## Validation evidence and limits

| Check | Recorded result |
| ----- | --------------- |
| Classic ESP32 configuration, current code | Valid with ESPHome 2026.9.1. |
| C3 configuration, current code | Valid with ESPHome 2026.9.1, including the local package merge. |
| C3 full firmware build, including year and language selection | Successful with ESPHome 2026.9.1, Python 3.12.13, ESP-IDF 5.5.5, and the Arduino framework. Flash: 1,037,494 / 1,835,008 bytes; reported RAM: 109,718 / 321,296 bytes. |
| Display simulation | Passes brightness/power handling, 2,880 schedule minutes, 14 icon frames, date timing/year, all seven weekdays in both languages with live switching, invalid time/temperature, and 8,000 text-animation frames. |
| Runtime settings simulation | Passes 6,343 timezone/DST comparisons with Python `zoneinfo`, plus sensor string lifetime, pending edits, invalid IDs, startup fallback, and save/restart handling. |
| Classic ESP32 full firmware build | An earlier configuration compiled with ESPHome 2026.10.0 before runtime settings were added. The latest classic ESP32 configuration has not been fully rebuilt in this work. |
| Physical hardware | Not verified by these software checks. No device was flashed during them. |

Build RAM figures do not measure runtime heap. The simulations do not prove flash persistence, physical rendering, electrical compatibility, Wi-Fi stability, Home Assistant reconnection, or browser behaviour. Hardware results should be added when available, identifying the board and ESPHome version.

## Upgrade requirements

Use ESPHome **2026.9.1 or newer**. The new runtime settings are implemented against ESPHome's parsed timezone API.

For a C3 installation, copy these files into the ESPHome configuration folder, often shown as `homeassistant/esphome/` and seen by ESPHome as `/config/esphome/`:

```text
max7219-esp32-reg.yaml
max7219-esp32c3-supermini.yaml
clock_settings.h
fonts/basis33.ttf
fonts/pixelmix.ttf
```

Keep the existing `secrets.yaml` and adjust the device's `!secret` references to match its key names. Compile and install the **C3** configuration. For a classic ESP32, compile the original entry point instead; it also needs `clock_settings.h`. Existing devices need one firmware update to expose the new controls. Later zone, language, and temperature-source changes use those controls.

## Files involved in the contribution

| File | Purpose |
| ---- | ------- |
| `max7219-esp32-reg.yaml` | Shared firmware, compatibility fixes, runtime controls, and date changes. |
| `max7219-esp32c3-supermini.yaml` | Alternative board entry point. |
| `clock_settings.h` | Runtime timezone and entity validation helper. |
| `secrets.example.yaml` | Credential template and existing-secret guidance. |
| `README.md` | Setup, wiring, and operating instructions. |
| `ESPHOME_VALIDATION.md` | Validation evidence and limits. |
| `scripts/check_display_logic.py` | Display simulation. |
| `scripts/check_runtime_settings.py` | Runtime settings tests. |
| `docs/FORK_CHANGES.md` | This summary of the fork's changes. |
| `docs/PULL_REQUEST_GUIDE.md` | First contribution workflow for this repository. |
| `docs/PULL_REQUEST_DESCRIPTION.md` | Suggested upstream PR title and description. |
| `docs/images/esphome-web-ui.png` | Screenshot of the C3 Web UI and runtime settings. |

The bundled fonts and original clock/setup images come from the original project. The Web UI screenshot was supplied during fork development.
