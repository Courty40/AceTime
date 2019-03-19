#include "common/util.h"
#include "LocalTime.h"

namespace ace_time {

using common::printPad2;

void LocalTime::printTo(Print& printer) const {
  if (isError()) {
    printer.print(F("<Invalid LocalTime>"));
    return;
  }

  // Time
  printPad2(printer, mHour);
  printer.print(':');
  printPad2(printer, mMinute);
  printer.print(':');
  printPad2(printer, mSecond);
}

LocalTime LocalTime::forTimeString(const char* ds) {
  if (strlen(ds) < kTimeStringLength) {
    return forError();
  }

  // hour
  uint8_t hour = (*ds++ - '0');
  hour = 10 * hour + (*ds++ - '0');

  // ':'
  ds++;

  // minute
  uint8_t minute = (*ds++ - '0');
  minute = 10 * minute + (*ds++ - '0');

  // ':'
  ds++;

  // second
  uint8_t second = (*ds++ - '0');
  second = 10 * second + (*ds++ - '0');

  return LocalTime(hour, minute, second);
}

}
