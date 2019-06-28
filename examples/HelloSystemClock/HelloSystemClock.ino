/*
 * A program to demonstrate the use of AceTime SystemClock. It should print the
 * following on the Serial port every 2 seconds:
 *
 *   2019-06-17T19:50:00-07:00[America/Los_Angeles]
 *   2019-06-17T19:50:02-07:00[America/Los_Angeles]
 *   2019-06-17T19:50:04-07:00[America/Los_Angeles]
 *   ...
 */

#include <AceTime.h>

using namespace ace_time;
using namespace ace_time::clock;

// ZoneSpecifier instance should be created statically at initialization time.
static BasicZoneSpecifier pacificSpec(&zonedb::kZoneAmerica_Los_Angeles);

SystemClock systemClock(nullptr /*sync*/, nullptr /*backup*/);
SystemClockHeartbeatLoop systemClockHeartbeat(systemClock);

//------------------------------------------------------------------

void setup() {
  delay(1000);
  Serial.begin(115200); // ESP8266 default of 74880 not supported on Linux
  while (!Serial); // Wait until Serial is ready - Leonardo/Micro

  systemClock.setup();

  // Creating timezones is cheap, so we can create them on the fly as needed.
  auto pacificTz = TimeZone::forZoneSpecifier(&pacificSpec);

  // Set the SystemClock using these components.
  auto pacificTime = ZonedDateTime::forComponents(
      2019, 6, 17, 19, 50, 0, pacificTz);
  systemClock.setNow(pacificTime.toEpochSeconds());
}

//------------------------------------------------------------------

void printCurrentTime() {
  acetime_t now = systemClock.getNow();

  // Create Pacific Time and print.
  auto pacificTz = TimeZone::forZoneSpecifier(&pacificSpec);
  auto pacificTime = ZonedDateTime::forEpochSeconds(now, pacificTz);
  pacificTime.printTo(Serial);
  Serial.println();
}

void loop() {
  printCurrentTime();
  systemClockHeartbeat.loop(); // must call every 65s or less
  delay(2000);
}