#pragma once

#include <string>
#include "esphome/components/time/posix_tz.h"

namespace matrix_clock {

// Rules use local wall time at the transition, as in the IANA/POSIX TZ database.
// Offsets follow POSIX convention: positive values are west of UTC.
inline esphome::time::DSTRule month_rule(unsigned month, unsigned week, unsigned hour) {
  esphome::time::DSTRule rule{};
  rule.type = esphome::time::DSTRuleType::MONTH_WEEK_DAY;
  rule.month = month;
  rule.week = week;
  rule.day_of_week = 0;  // Sunday
  rule.time_seconds = hour * 3600;
  return rule;
}

inline bool apply_timezone(const std::string &name) {
  esphome::time::ParsedTimezone zone{};
  if (name == "UTC") {
    zone.std_offset_seconds = 0;
  } else if (name == "Australia/Sydney" || name == "Australia/Melbourne" || name == "Australia/Hobart") {
    zone.std_offset_seconds = -10 * 3600;
    zone.dst_offset_seconds = -11 * 3600;
    zone.dst_start = month_rule(10, 1, 2);
    zone.dst_end = month_rule(4, 1, 3);
  } else if (name == "Australia/Adelaide") {
    zone.std_offset_seconds = -(9 * 3600 + 1800);
    zone.dst_offset_seconds = -(10 * 3600 + 1800);
    zone.dst_start = month_rule(10, 1, 2);
    zone.dst_end = month_rule(4, 1, 3);
  } else if (name == "Australia/Lord_Howe") {
    zone.std_offset_seconds = -(10 * 3600 + 1800);
    zone.dst_offset_seconds = -11 * 3600;
    zone.dst_start = month_rule(10, 1, 2);
    zone.dst_end = month_rule(4, 1, 2);
  } else if (name == "Australia/Brisbane") {
    zone.std_offset_seconds = -10 * 3600;
  } else if (name == "Australia/Darwin") {
    zone.std_offset_seconds = -(9 * 3600 + 1800);
  } else if (name == "Australia/Perth" || name == "Asia/Singapore") {
    zone.std_offset_seconds = -8 * 3600;
  } else if (name == "Pacific/Auckland") {
    zone.std_offset_seconds = -12 * 3600;
    zone.dst_offset_seconds = -13 * 3600;
    zone.dst_start = month_rule(9, 5, 2);
    zone.dst_end = month_rule(4, 1, 3);
  } else if (name == "Europe/Berlin") {
    zone.std_offset_seconds = -3600;
    zone.dst_offset_seconds = -2 * 3600;
    zone.dst_start = month_rule(3, 5, 2);
    zone.dst_end = month_rule(10, 5, 3);
  } else if (name == "Europe/London") {
    zone.std_offset_seconds = 0;
    zone.dst_offset_seconds = -3600;
    zone.dst_start = month_rule(3, 5, 1);
    zone.dst_end = month_rule(10, 5, 2);
  } else if (name == "America/New_York" || name == "America/Chicago" ||
             name == "America/Denver" || name == "America/Los_Angeles") {
    const int hours = name == "America/New_York" ? 5 : name == "America/Chicago" ? 6 :
                      name == "America/Denver" ? 7 : 8;
    zone.std_offset_seconds = hours * 3600;
    zone.dst_offset_seconds = (hours - 1) * 3600;
    zone.dst_start = month_rule(3, 2, 2);
    zone.dst_end = month_rule(11, 1, 2);
  } else if (name == "Asia/Tokyo") {
    zone.std_offset_seconds = -9 * 3600;
  } else if (name == "Asia/Kolkata") {
    zone.std_offset_seconds = -(5 * 3600 + 1800);
  } else {
    return false;  // Leave the active zone unchanged for an unsupported name.
  }
  esphome::time::set_global_tz(zone);
  return true;
}

inline bool valid_temperature_entity(const std::string &value) {
  if (value.size() <= 7 || value.size() > 100 || value.compare(0, 7, "sensor.") != 0)
    return false;
  for (size_t i = 7; i < value.size(); ++i) {
    const char c = value[i];
    if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_'))
      return false;
  }
  return true;
}

}  // namespace matrix_clock
