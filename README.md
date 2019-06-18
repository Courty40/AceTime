# AceTime

This library provides date and time classes for the Arduino platform with
support for geographical time zones in the [IANA TZ
database](https://www.iana.org/time-zones). Date and time from one timezone can
be converted to another timezone. The library also provides a
SystemClock that can be synchronized from a more reliable external time
source, such as an [NTP](https://en.wikipedia.org/wiki/Network_Time_Protocol)
server or a [DS3231
RTC](https://www.maximintegrated.com/en/products/analog/real-time-clocks/DS3231.html)
chip. This library is meant to be an alternative to the [Arduino
Time](https://github.com/PaulStoffregen/Time) and [Arduino
Timezone](https://github.com/JChristensen/Timezone) libraries.

The AceTime classes are organized into roughly 4 bundles, placed in different
C++ namespaces:

* date and time classes
    * `ace_time::LocalTime`
    * `ace_time::LocalDate`
    * `ace_time::LocalDateTime`
    * `ace_time::TimeOffset`
    * `ace_time::OffsetDateTime`
    * `ace_time::ZoneSpecifier`
        * `ace_time::ManualZoneSpecifier`
        * `ace_time::BasicZoneSpecifier`
        * `ace_time::ExtendedZoneSpecifier`
    * `ace_time::TimeZone`
    * `ace_time::ZonedDateTime`
    * `ace_time::TimePeriod`
    * mutation helpers
        * `ace_time::date_time_mutation::*`
        * `ace_time::local_date_mutation::*`
        * `ace_time::time_offset_mutation::*`
        * `ace_time::time_period_mutation::*`
* system clock classes
    * `ace_time::clock::TimeProvider`
        * `ace_time::clock::TimeKeeper`
            * `ace_time::clock::SystemClock`
            * `ace_time::clock::DS3231TimeKeeper`
        * `ace_time::clock::NtpTimeProvider`
    * `ace_time::clock::SystemClockHeartbeatCoroutine`
    * `ace_time::clock::SystemClockHeartbeatLoop`
    * `ace_time::clock::SystemClockSyncCoroutine`
    * `ace_time::clock::SystemClockSyncLoop`
* TZ Database zone files
    * C++ files generated by a code-generator from the TZ Database zone files
    * `ace_time::zonedb` (231 timezones)
        * Used by `BasicZoneSpecifier`
        * `zonedb::kZoneAfrica_Abidjan`
        * `zonedb::kZoneAfrica_Accra`
        * ...227 other zones...
        * `zonedb::kZonePacific_Wake`
        * `zonedb::kZonePacific_Wallis`
    * `ace_time::zonedbx` (348 timezones)
        * Used by `ExtendedZoneSpecifier`
        * `zonedbx::kZoneAfrica_Abidjan`
        * `zonedbx::kZoneAfrica_Accra`
        * ...344 other zones...
        * `zonedbx::kZonePacific_Wake`
        * `zonedbx::kZonePacific_Wallis`
* Helper and common classes
    * `ace_time::acetime_t`
    * `ace_time::common::DateStrings`
    * `ace_time::common::ZoneContext`
    * `ace_time::basic::ZoneInfo`
    * `ace_time::basic::ZoneEra`
    * `ace_time::basic::ZonePolicy`
    * `ace_time::basic::ZoneRule`
    * `ace_time::extended::ZoneInfo`
    * `ace_time::extended::ZoneEra`
    * `ace_time::extended::ZonePolicy`
    * `ace_time::extended::ZoneRule`

The "date and time" classes provide a thin abstraction layer to make it easier
to use and manipulate date and time fields. For example, each of the
`LocalDateTime`, `OffsetDateTime` and `ZonedDateTime` classes provide the
`dayOfWeek()` method which returns the day of the week of the given date; the
`toEpochSeconds()` which returns the number of seconds from a epoch date; and
the `fromEpochSeconds()` which constructs the date and time fields from the
epoch seconds. The Epoch in AceTime is defined to be 2000-01-01T00:00:00Z,
in contrast to the Epoch in Unix which is 1970-01-01T00:00:00Z. Internally, the
current time is represented as "seconds from Epoch" which is a 32-bit signed
integer. The maximum date that AceTime can handle is 2068-01-19T03:14:07Z
(unlike 32-bit Unix whose maximum is 2038-01-19T03:14:07Z.) The `ZonedDateTime`
class works with the `TimeZone` class to provide access to the TZ Database and
allow conversions to other timezones using the
`ZonedDateTime::convertToTimeZone()` method.

The `ace_time::clock` classes collaborate together to implement the
SystemClock which can obtain its time from various sources, such as a DS3231 RTC
chip, or an Network Time Protocol (NTP) server. Retrieving the current time
from accurate clock sources can be expensive, so the `SystemClock` uses the
built-in `millis()` function to provide fast access to a reasonably accurate
clock, but synchronizes to more accurate clocks periodically.

The library provides 2 sets of "zone files" created from the IANA TZ Database:
* 231 zones generated in the `zonedb::` namespace which have (relatively) simple
  time zone transition rules, and intended to be used by `BasicZoneSpecifier`
  class, and
* 348 zones generated in the `zonedbx::` namespace which contain nearly all the
  zones in the TZ Database, intended to be used by the `ExtendedZoneSpecifier`
  class.

Both of these data sets have been unit tested from year 2000 to 2049
(inclusive). Custom datasets with smaller or larger range of years may be
generated by developers using scripts provided in this library. The target
application may be compiled against the custom dataset instead of using
`zonedb::` and `zonedbx::` zone files provided in this library.

Version: 0.1 (2019-06-15)

## HelloTime

Here is a simple program (see [examples/HelloTime](examples/HelloTime)) which
demonstrates how to create and manipulate date and times in different time
zones:

```C++
#include <AceTime.h>

using namespace ace_time;

// ZoneSpecifier instances should be created statically at initialization time.
static BasicZoneSpecifier pacificSpec(&zonedb::kZoneAmerica_Los_Angeles);
static BasicZoneSpecifier easternSpec(&zonedb::kZoneAmerica_New_York);
static ExtendedZoneSpecifier turkeySpec(&zonedbx::kZoneEurope_Istanbul);

void setup() {
  delay(1000);
  Serial.begin(115200); // ESP8266 default of 74880 not supported on Linux
  while (!Serial); // Wait until Serial is ready - Leonardo/Micro

  auto pacificTz = TimeZone::forZoneSpecifier(&pacificSpec);
  auto easternTz = TimeZone::forZoneSpecifier(&easternSpec);
  auto turkeyTz = TimeZone::forZoneSpecifier(&turkeySpec);

  // Create from components
  auto pacificTime = ZonedDateTime::forComponents(
      2019, 6, 1, 11, 38, 0, pacificTz);

  Serial.print(F("America/Los_Angeles: "));
  pacificTime.printTo(Serial);
  Serial.println();

  Serial.print(F("Epoch Seconds: "));
  acetime_t epochSeconds = pacificTime.toEpochSeconds();
  Serial.println(epochSeconds);

  Serial.print(F("Unix Seconds: "));
  acetime_t unixSeconds = pacificTime.toUnixSeconds();
  Serial.println(unixSeconds);

  // Create from epoch seconds
  auto easternTime = ZonedDateTime::forEpochSeconds(epochSeconds, easternTz);

  Serial.print(F("America/New_York: "));
  easternTime.printTo(Serial);
  Serial.println();

  // Create by conversion to time zone
  auto turkeyTime = easternTime.convertToTimeZone(turkeyTz);

  Serial.print(F("Europe/Istanbul: "));
  turkeyTime.printTo(Serial);
  Serial.println();

  Serial.print(F("pacificTime.compareTo(turkeyTime): "));
  Serial.println(pacificTime.compareTo(turkeyTime));

  Serial.print(F("pacificTime == turkeyTime: "));
  Serial.println((pacificTime == turkeyTime) ? "true" : "false");
}

void loop() {
}
```

Running this should produce the following on the Serial port:
```
 America/Los_Angeles: 2019-06-01T11:38:00-07:00 Saturday [America/Los_Angeles]
 Epoch Seconds: 612729480
 Unix Seconds: 1559414280
 America/New_York: 2019-06-01T14:38:00-04:00 Saturday [America/New_York]
 Europe/Istanbul: 2019-06-01T21:38:00+03:00 Saturday [Europe/Istanbul]
 pacific.compareTo(turkey): 0
 pacific == turkey: false
```

## HelloSystemClock

This is the example code for using the `SystemClock` taken from
[HelloSystemClock](examples/HelloSystemClock/).

```C++
#include <AceTime.h>

using namespace ace_time;
using namespace ace_time::clock;

// ZoneSpecifier instances should be created statically at initialization time.
static BasicZoneSpecifier pacificSpec(&zonedb::kZoneAmerica_Los_Angeles);
static BasicZoneSpecifier easternSpec(&zonedb::kZoneAmerica_New_York);

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
  Serial.print(F("Pacific Time: "));
  pacificTime.printTo(Serial);
  Serial.println();

  // Convert to Eastern Time and print.
  auto easternTz = TimeZone::forZoneSpecifier(&easternSpec);
  auto easternTime = pacificTime.convertToTimeZone(easternTz);
  Serial.print(F("Eastern Time: "));
  easternTime.printTo(Serial);
  Serial.println();

  Serial.println();
}

void loop() {
  printCurrentTime();
  systemClockHeartbeat.loop(); // must call every 65s or less
  delay(2000);
}
```

This will start by setting the SystemClock to 2019-06-17T19:50:00-07:00,
then printing the system time every 2 seconds in 2 time zones:
```
Pacific Time: 2019-06-17T19:50:00-07:00 Monday [America/Los_Angeles]
Eastern Time: 2019-06-17T22:50:00-04:00 Monday [America/New_York]

Pacific Time: 2019-06-17T19:50:02-07:00 Monday [America/Los_Angeles]
Eastern Time: 2019-06-17T22:50:02-04:00 Monday [America/New_York]

Pacific Time: 2019-06-17T19:50:04-07:00 Monday [America/Los_Angeles]
Eastern Time: 2019-06-17T22:50:04-04:00 Monday [America/New_York]
```

## User Guide

See the [AceTime User Guide](USER_GUIDE.md) for information on:
* Installation
* Date and Time classes
* System Clock classes
* Benchmarks
* Comparison to Other Libraries
* Bugs and Limitations

## System Requirements

This library was developed and tested using:

* [Arduino IDE 1.8.9](https://www.arduino.cc/en/Main/Software)
* [ESP8266 Arduino Core 2.5.1](https://github.com/esp8266/Arduino)
* [ESP32 Arduino Core 1.0.2](https://github.com/espressif/arduino-esp32)

I used Ubuntu 18.04 for most of my development.

The library is tested on the following hardware before each release:

* Arduino Nano clone (16 MHz ATmega328P)
* Arduino Pro Micro clone (16 MHz ATmega32U4)
* WeMos D1 Mini clone (ESP-12E module, 80 MHz ESP8266)
* ESP32 dev board (ESP-WROOM-32 module, 240 MHz dual core Tensilica LX6)

I will occasionally test on the following hardware as a sanity check:

* Teensy 3.2 (72 MHz ARM Cortex-M4)

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT License](https://opensource.org/licenses/MIT)

## Feedback and Support

If you have any questions, comments, bug reports, or feature requests, please
file a GitHub ticket instead of emailing me unless the content is sensitive.
(The problem with email is that I cannot reference the email conversation when
other people ask similar questions later.) I'd love to hear about how this
software and its documentation can be improved. I can't promise that I will
incorporate everything, but I will give your ideas serious consideration.

## Authors

Created by Brian T. Park (brian@xparks.net).
