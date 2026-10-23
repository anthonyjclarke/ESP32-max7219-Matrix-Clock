# ESPHome Validation

The original configuration was checked on 22 October 2026 against ESPHome `2026.10.0`, using Python `3.12.14`, the `esp32dev` board, Arduino `3.3.12`, and ESP-IDF `5.5.6`. See the runtime settings section below for checks of the updated configuration on 23 October.

---

## Result

The original corrected `max7219-esp32-reg.yaml` passed ESPHome configuration validation and a complete ESP32 firmware build. Compilation used temporary test credentials in an isolated directory. No device was connected or flashed. These original build results predate the runtime settings changes.

The build reported flash usage of 968,307 bytes out of 1,835,008 bytes (52.8%), and static RAM usage of 49,932 bytes out of the reported 180,736-byte budget (27.6%). These figures do not measure runtime heap usage or prove stability on hardware.

The repository contains the tested source and configuration template. Generate firmware again with your own credentials before installing it.

---

## Issues Found and Fixed

### Captive Portal Configuration

The original `captive_portal` entry was nested inside `wifi.ap`. ESPHome rejected it as an invalid option. It is now a top-level component, as required by the [ESPHome captive portal configuration](https://esphome.io/components/captive_portal/).

### Credentials and API Key

The original `DEIN_API_KEY` placeholder failed ESPHome's base64 key validation. The device configuration now uses `!secret` references, and `secrets.example.yaml` contains the corresponding key/value entries. Its API key placeholder must be replaced with a unique base64-encoded 32-byte key. Use `openssl rand -base64 32` to generate one.

The old example file contained complete ESPHome component sections rather than a usable secrets mapping. It is now a template that can be copied to `secrets.yaml`, or merged into an existing Home Assistant secrets file. No real credentials were used or added to the repository.

### Runtime Brightness Updates

In the MAX7219 matrix driver, `set_intensity()` only updates the stored intensity value. The runtime `intensity()` method also transmits the command to the chips. The rendering lambda now uses `intensity()` when the target brightness changes, following the [documented MAX7219 intensity interface](https://esphome.io/components/display/max7219digit/#max7219intensity-action).

The direct brightness and power callbacks were removed. The display lambda applies the current power and day/night settings together on the next 50 ms frame, keeping its brightness cache consistent and preventing the daytime slider from overriding night brightness.

### Text Animation

The driver's built-in scrolling is enabled by default. It could scroll the extended buffer while the custom lambda was already animating the same text. The configuration now sets `scroll_enable: false` so that the custom Scroll, Bounce, Wipe, and Static modes control positioning.

### Unavailable Temperature

The temperature display now checks that the sensor value is finite, as well as checking that a state exists. Unavailable or invalid readings display `--.-°` instead of `nan°`.

---

## Software Checks Completed

ESPHome configuration validation and the full firmware build both completed successfully. The bundled TrueType fonts were loaded successfully; their digit and text glyph heights fit the intended eight-pixel display height.

The script `scripts/check_display_logic.py` extracts and executes the actual display lambda using simulated ESPHome entities and a recording display. It checks:

- Brightness changes, cached updates, blank night mode, and power off/on transitions.
- Every minute of an overnight schedule and a same-day schedule, covering 2,880 simulated minutes.
- All seven icons in both animation phases, with icon coordinates inside the 96×8 canvas.
- Date display timing at seconds `:50`–`:55`, inclusive, and the unsynchronised clock state.
- Invalid temperature handling and empty or short text.
- Scroll, Bounce, Wipe, and Static modes over 8,000 simulated frames.

The simulation verifies control flow and icon coordinates. It does not emulate the MAX7219 electrical interface, font rasterisation, Wi-Fi, SNTP, Home Assistant, or the complete ESP32 runtime.

ESPHome emitted an advisory recommending encrypted OTA instead of the existing OTA password mechanism. The password mechanism remains accepted and compiled successfully.

---

## Repeating the Checks

After creating `secrets.yaml` with your own values, use an ESPHome `2026.10.0` environment to run:

```sh
esphome config max7219-esp32-reg.yaml
esphome compile max7219-esp32-reg.yaml
```

The host simulation requires Python 3 and either `clang++` or `g++`:

```sh
python3 scripts/check_display_logic.py
```

---

## Before the First Hardware Test

1. Select the configuration for your board: `max7219-esp32-reg.yaml` for a classic ESP32 compatible with `esp32dev`, or `max7219-esp32c3-supermini.yaml` for the alternative C3 SuperMini described below. Other variants need their own board configuration and suitable pins.
2. Confirm that the display has 12 chained MAX7219 8×8 modules, matching `num_chips: 12` and the 96×8 drawing coordinates.
3. Check the regulated 5 V supply, current capacity, shared ground, and logic-level requirements. For the classic ESP32, confirm `GPIO26` → `CLK`, `GPIO27` → `DIN`, and `GPIO25` → `CS`. For the C3 alternative, use `GPIO6` → `CLK`, `GPIO7` → `DIN`, and `GPIO10` → `CS`, with level buffering as described in the README.
4. Enter your Wi-Fi and API/OTA credentials and copy `clock_settings.h` beside the device YAML files. The clock needs network access for SNTP; temperature requires the Home Assistant API connection.
5. After installation, select **Time Zone**, set **Temperature Entity**, and press **Apply Sensor (Restart)** to apply the sensor subscription. The initial zone is `Europe/Berlin`; `Australia/Sydney` is suitable for Sydney. **Weekday Language** defaults to German and can be changed to English while running.
6. After flashing, check module rotation/order, clock and date readability, temperature, all text modes, daytime brightness, night blanking, and power off/on. Use `rotate_chip`, `reverse_enable`, or `flip_x` if required by your module orientation.

The software is ready for a hardware trial after these installation values are configured. Correct wiring, supply quality, physical display orientation, network connectivity, and behaviour on the actual device remain unverified until that trial.

---

## ESP32-C3 SuperMini Alternative

Added on 23 October 2026. The alternative `max7219-esp32c3-supermini.yaml` includes the classic configuration as a local package and overrides the board/variant, device name, SPI/display pins, native USB logging, and fallback hotspot name. The display lambda and Home Assistant entities are shared. See the [C3 setup instructions](./README.md#alternative-device-esp32-c3-supermini) for wiring and installation.

The display logic simulation passes with the shared rendering code. The alternative configuration, including its package merge and runtime settings, passes ESPHome `2026.9.1` configuration validation using temporary test credentials in an isolated directory. Firmware build results are recorded in the runtime settings section below. USB and physical display operation remain untested. The original classic ESP32 memory figures above are historical results for that target, not C3 results.

Before the C3 hardware trial, configure your secrets and run:

```sh
esphome config max7219-esp32c3-supermini.yaml
esphome compile max7219-esp32c3-supermini.yaml
```

Physical checks remain pending: USB flashing/logging, Wi-Fi and Home Assistant connection, display orientation and all rendering modes, brightness/night blanking, cold boot from the intended supply, and OTA updates.

---

## Runtime Time Zone and Temperature Settings

Added on 23 October 2026. Both board configurations now expose a saved **Time Zone** select, a saved **Temperature Entity** text field, and an **Apply Sensor (Restart)** button. The time zone updates immediately using ESPHome's parsed timezone API; the sensor is bound before its startup subscription, using a string owned for the entire boot. Applying the sensor flushes pending preferences before restarting. Invalid entity names or a failed flash sync cancel that restart.

The configuration requires ESPHome `2026.9.1` or newer and the local `clock_settings.h` header. ESPHome `2026.9.1` configuration validation passes for both the classic ESP32 and C3 using temporary credentials. The existing display simulation passes, including all four text modes and day/night schedule checks.

The complete C3 firmware build also passes with ESPHome `2026.9.1`, Python `3.12.13`, the `esp32-c3-devkitm-1` target, and ESP-IDF `5.5.5` with the Arduino framework. The latest build, including the date year and weekday language changes below, reports flash usage of 1,037,494 / 1,835,008 bytes (56.5%) and RAM usage of 109,718 / 321,296 bytes (34.1%). These are build figures, not runtime heap measurements. No hardware was flashed, and the new classic ESP32 configuration was validated but was not rebuilt in this check. Temporary test credentials were used only in an isolated directory; rebuild with your own credentials before installation.

`scripts/check_runtime_settings.py` compiles the actual settings header and startup/apply lambdas with a recording sensor, preferences, and application. It links ESPHome's actual `posix_tz.cpp` converter and compares 6,343 local time/DST cases against Python `zoneinfo`: all 19 dropdown zones, 2024/2026/2030 dates, leap day, and the second before/at/after every 2026 DST transition. It also checks subscription-string lifetime while editing, applying after a successful save, invalid entity names, maximum entity length, startup fallback, and cancelling restart on save failure.

Run in an ESPHome Python environment with `clang++` or `g++`:

```sh
python3 scripts/check_display_logic.py
python3 scripts/check_runtime_settings.py
```

These checks do not emulate flash persistence, the Home Assistant API transport, browser controls, or the complete hardware runtime. On hardware, verify that both controls appear, selected zones restore after restart, the night schedule follows local time, and switching between two known temperature entities receives the new source after applying. Also verify recovery from a missing/unavailable entity and from a Home Assistant reconnect.

## Date Year and Weekday Language

The date now includes the four-digit year (`DD.MM.YYYY`). A saved **Weekday Language** selector defaults to **German** (`SO MO DI MI DO FR SA`) and offers **English** (`SU MO TU WE TH FR SA`), Sunday through Saturday. The display reads this selection on every date frame, so switching languages requires no restart.

The display simulation passes for all seven weekdays in both languages, switching languages on the running date page, the full date including the year, and the existing seconds `:50`–`:55` timing. Font metrics for the bundled eight-pixel `pixelmix` font give a maximum date width of 67 pixels in either language, fitting from X=4 before the calendar icon at X=87. Physical rendering and restoring the language after a power cycle still need hardware verification.
