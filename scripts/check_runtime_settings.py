"""Exercise runtime settings against ESPHome's real timezone converter.

Run in an ESPHome 2026.9.1+ Python environment with clang++ or g++ installed.
No device or real credentials are required.
"""

from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile
from zoneinfo import ZoneInfo

import esphome
import yaml


class Loader(yaml.SafeLoader):
    pass


Loader.add_constructor('!secret', lambda loader, node: loader.construct_scalar(node))
root = Path(__file__).resolve().parents[1]
config = yaml.load((root / 'max7219-esp32-reg.yaml').read_text(), Loader=Loader)
timezone_control = next(item for item in config['select'] if item['id'] == 'clock_timezone')
entity_control = next(item for item in config['text'] if item['id'] == 'temperature_entity')
assert timezone_control['restore_value'] and entity_control['restore_value']
boot = config['esphome']['on_boot'][0]
assert 100 < boot['priority'] < 800, 'Entity must bind after text restore and before HA subscription'
startup = boot['then'][0]['lambda']
for key, value in config['substitutions'].items():
    startup = startup.replace('${' + key + '}', value)
apply = config['button'][0]['on_press']['then'][0]['lambda']
esphome_root = Path(esphome.__file__).resolve().parent.parent

harness = r'''
#include <cassert>
#include <cmath>
#include <iostream>
#include <string>
#include "clock_settings.h"
#define id(x) x
#define ESP_LOGW(...) ((void) 0)
#define ESP_LOGE(...) ((void) 0)
struct Text { std::string state; } temperature_entity;
std::string active_temperature_entity;
struct Sensor {
  const char *entity = nullptr;
  void set_entity_id(const char *value) { entity = value; }
} temp_sensor;
bool saved = false, rebooted = false;
struct Preferences {
  bool success = true;
  bool sync() { saved = success; return success; }
} preferences;
auto *global_preferences = &preferences;
struct Application {
  void safe_reboot() { assert(saved); rebooted = true; }
} App;
void startup() {
__STARTUP__
}
void apply() {
__APPLY__
}
int main() {
  temperature_entity.state = "sensor.outdoor_temperature";
  startup();
  assert(std::string(temp_sensor.entity) == temperature_entity.state);
  const char *subscription_pointer = temp_sensor.entity;
  temperature_entity.state = "sensor.another_temperature_with_a_longer_entity_name";
  assert(temp_sensor.entity == subscription_pointer);
  assert(std::string(temp_sensor.entity) == "sensor.outdoor_temperature");
  apply(); assert(saved && rebooted);
  startup(); assert(std::string(temp_sensor.entity) == temperature_entity.state);
  saved = rebooted = false;
  preferences.success = false;
  apply(); assert(!saved && !rebooted);
  preferences.success = true;
  for (const char *value : {"", "sensor.", "weather.home", "sensor.bad name",
                           "sensor.UPPER", "sensor.bad\n", "sensor.bad-name"}) {
    temperature_entity.state = value;
    apply(); assert(!saved && !rebooted);
    startup();
    assert(std::string(temp_sensor.entity) == "__DEFAULT_ENTITY__");
  }
  assert(matrix_clock::valid_temperature_entity("sensor.a_012"));
  assert(matrix_clock::valid_temperature_entity("sensor." + std::string(93, 'x')));
  assert(!matrix_clock::valid_temperature_entity("sensor." + std::string(94, 'x')));
  assert(matrix_clock::apply_timezone("Australia/Sydney"));
  assert(!matrix_clock::apply_timezone("Unsupported/Zone"));
  assert(esphome::time::get_global_tz().std_offset_seconds == -36000);
  std::string zone;
  long long epoch;
  int year, month, day, hour, minute, second, dst;
  unsigned count = 0;
  while (std::cin >> zone >> epoch >> year >> month >> day >> hour >> minute >> second >> dst) {
    assert(matrix_clock::apply_timezone(zone));
    std::tm actual{};
    assert(esphome::time::epoch_to_local_tm(epoch, esphome::time::get_global_tz(), &actual));
    if (actual.tm_year + 1900 != year || actual.tm_mon + 1 != month || actual.tm_mday != day ||
        actual.tm_hour != hour || actual.tm_min != minute || actual.tm_sec != second ||
        actual.tm_isdst != dst) {
      std::cerr << "Timezone mismatch: " << zone << " at UTC epoch " << epoch << '\n';
      return 1;
    }
    count++;
  }
  std::cout << "PASS: " << count << " timezone/DST cases against zoneinfo; entity binding, "
               "pending edits, invalid inputs, save-before-restart, and save failure.\n";
}
'''
harness = harness.replace('__STARTUP__', startup).replace('__APPLY__', apply)
harness = harness.replace('__DEFAULT_ENTITY__', config['substitutions']['default_temperature_entity'])

cases = []
for name in timezone_control['options']:
    zone = ZoneInfo(name)
    epochs = set()
    for year in (2024, 2026, 2030):
        for month in range(1, 13):
            for day in (1, 15, 28):
                for hour in (0, 12, 23):
                    epochs.add(int(datetime(year, month, day, hour, tzinfo=timezone.utc).timestamp()))
    epochs.add(int(datetime(2024, 2, 29, 23, 59, 59, tzinfo=timezone.utc).timestamp()))
    # Locate every 2026 offset transition, then test both sides to the second.
    previous = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(2027, 1, 1, tzinfo=timezone.utc).timestamp())
    offset = lambda epoch: datetime.fromtimestamp(epoch, zone).utcoffset()
    while previous < end:
        current = previous + 6 * 3600
        if offset(previous) != offset(current):
            lo, hi = previous, current
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if offset(mid) == offset(previous):
                    lo = mid
                else:
                    hi = mid
            epochs.update(hi + delta for delta in (-86400, -3600, -1, 0, 1, 3600, 86400))
        previous = current
    for epoch in sorted(epochs):
        local = datetime.fromtimestamp(epoch, zone)
        cases.append(f'{name} {epoch} {local.year} {local.month} {local.day} '
                     f'{local.hour} {local.minute} {local.second} {int(bool(local.dst()))}\n')

compiler = shutil.which('clang++') or shutil.which('g++')
if not compiler:
    raise SystemExit('Install clang++ or g++ to run these checks.')
with tempfile.TemporaryDirectory(prefix='matrix-clock-settings-') as directory:
    temp = Path(directory)
    defines = temp / 'esphome/core/defines.h'
    defines.parent.mkdir(parents=True)
    defines.write_text('#ifndef USE_TIME_TIMEZONE\n#define USE_TIME_TIMEZONE\n#endif\n')
    source = temp / 'runtime_settings.cpp'
    source.write_text(harness)
    executable = temp / 'runtime_settings'
    subprocess.run([compiler, '-std=c++17', '-DUSE_TIME_TIMEZONE', '-I', str(temp),
                    '-I', str(root), '-I', str(esphome_root), str(source),
                    str(esphome_root / 'esphome/components/time/posix_tz.cpp'),
                    '-o', str(executable)], check=True)
    subprocess.run([str(executable)], input=''.join(cases), text=True, check=True)
