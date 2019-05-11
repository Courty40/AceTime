#line 2 "LocalDateTimeTest.ino"

#include <AUnit.h>
#include <AceTime.h>

using namespace aunit;
using namespace ace_time;
using namespace ace_time::common;

// --------------------------------------------------------------------------
// LocalDate
// --------------------------------------------------------------------------

test(LocalDateTest, accessors) {
  LocalDate ld = LocalDate::forComponents(2001, 2, 3);
  assertEqual((int16_t) 2001, ld.year());
  assertEqual(2, ld.month());
  assertEqual(3, ld.day());
}

test(LocalDateTest, isError) {
  assertFalse(LocalDate::forComponents(0, 1, 1).isError());
  assertFalse(LocalDate::forComponents(0, 1, 31).isError());
  assertFalse(LocalDate::forComponents(0, 2, 30).isError());
  assertFalse(LocalDate::forComponents(0, 2, 31).isError());
  assertFalse(LocalDate::forComponents(0, 12, 31).isError());

  assertTrue(LocalDate::forComponents(0, 0, 1).isError());
  assertTrue(LocalDate::forComponents(0, 1, 0).isError());
  assertTrue(LocalDate::forComponents(0, 1, 32).isError());
  assertTrue(LocalDate::forComponents(0, 13, 1).isError());
}

// Verify that toEpochDays()/forEpochDays() and
// toEpochSeconds()/forEpochSeconds() support round trip conversions when when
// isError()==true.
test(LocalDateTest, forError) {
  LocalDate ld;

  ld = LocalDate::forError();
  assertTrue(ld.isError());
  assertEqual(LocalDate::kInvalidEpochDays, ld.toEpochDays());
  assertEqual(LocalDate::kInvalidEpochSeconds, ld.toEpochSeconds());

  ld = LocalDate::forEpochDays(LocalDate::kInvalidEpochDays);
  assertTrue(ld.isError());

  ld = LocalDate::forEpochSeconds(LocalDate::kInvalidEpochSeconds);
  assertTrue(ld.isError());
}

test(LocalDateTest, dayOfWeek) {
  // year 1900 (not leap year due to every 100 rule)
  assertEqual(LocalDate::kWednesday,
      LocalDate::forComponents(1900, 2, 28).dayOfWeek());
  assertEqual(LocalDate::kThursday,
      LocalDate::forComponents(1900, 3, 1).dayOfWeek());

  // year 1999 was not a leap year
  assertEqual(LocalDate::kFriday,
      LocalDate::forComponents(1999, 1, 1).dayOfWeek());
  assertEqual(LocalDate::kSunday,
      LocalDate::forComponents(1999, 1, 31).dayOfWeek());

  // year 2000 (leap year due to every 400 rule)
  assertEqual(LocalDate::kSaturday,
      LocalDate::forComponents(2000, 1, 1).dayOfWeek());
  assertEqual(LocalDate::kMonday,
      LocalDate::forComponents(2000, 1, 31).dayOfWeek());

  assertEqual(LocalDate::kTuesday,
      LocalDate::forComponents(2000, 2, 1).dayOfWeek());
  assertEqual(LocalDate::kTuesday,
      LocalDate::forComponents(2000, 2, 29).dayOfWeek());

  assertEqual(LocalDate::kWednesday,
      LocalDate::forComponents(2000, 3, 1).dayOfWeek());
  assertEqual(LocalDate::kFriday,
      LocalDate::forComponents(2000, 3, 31).dayOfWeek());

  assertEqual(LocalDate::kSaturday,
      LocalDate::forComponents(2000, 4, 1).dayOfWeek());
  assertEqual(LocalDate::kSunday,
      LocalDate::forComponents(2000, 4, 30).dayOfWeek());

  assertEqual(LocalDate::kMonday,
      LocalDate::forComponents(2000, 5, 1).dayOfWeek());
  assertEqual(LocalDate::kWednesday,
      LocalDate::forComponents(2000, 5, 31).dayOfWeek());

  assertEqual(LocalDate::kThursday,
      LocalDate::forComponents(2000, 6, 1).dayOfWeek());
  assertEqual(LocalDate::kFriday,
      LocalDate::forComponents(2000, 6, 30).dayOfWeek());

  assertEqual(LocalDate::kSaturday,
      LocalDate::forComponents(2000, 7, 1).dayOfWeek());
  assertEqual(LocalDate::kMonday,
      LocalDate::forComponents(2000, 7, 31).dayOfWeek());

  assertEqual(LocalDate::kTuesday,
      LocalDate::forComponents(2000, 8, 1).dayOfWeek());
  assertEqual(LocalDate::kThursday,
      LocalDate::forComponents(2000, 8, 31).dayOfWeek());

  assertEqual(LocalDate::kFriday,
      LocalDate::forComponents(2000, 9, 1).dayOfWeek());
  assertEqual(LocalDate::kSaturday,
      LocalDate::forComponents(2000, 9, 30).dayOfWeek());

  assertEqual(LocalDate::kSunday,
      LocalDate::forComponents(2000, 10, 1).dayOfWeek());
  assertEqual(LocalDate::kTuesday,
      LocalDate::forComponents(2000, 10, 31).dayOfWeek());

  assertEqual(LocalDate::kWednesday,
      LocalDate::forComponents(2000, 11, 1).dayOfWeek());
  assertEqual(LocalDate::kThursday,
      LocalDate::forComponents(2000, 11, 30).dayOfWeek());

  assertEqual(LocalDate::kFriday,
      LocalDate::forComponents(2000, 12, 1).dayOfWeek());
  assertEqual(LocalDate::kSunday,
      LocalDate::forComponents(2000, 12, 31).dayOfWeek());

  // year 2001
  assertEqual(LocalDate::kMonday,
      LocalDate::forComponents(2001, 1, 1).dayOfWeek());
  assertEqual(LocalDate::kWednesday,
      LocalDate::forComponents(2001, 1, 31).dayOfWeek());

  // year 2004 (leap year)
  assertEqual(LocalDate::kSunday,
      LocalDate::forComponents(2004, 2, 1).dayOfWeek());
  assertEqual(LocalDate::kSunday,
      LocalDate::forComponents(2004, 2, 29).dayOfWeek());
  assertEqual(LocalDate::kMonday,
      LocalDate::forComponents(2004, 3, 1).dayOfWeek());

  // year 2099
  assertEqual(LocalDate::kThursday,
      LocalDate::forComponents(2099, 1, 1).dayOfWeek());
  assertEqual(LocalDate::kThursday,
      LocalDate::forComponents(2099, 12, 31).dayOfWeek());

  // year 2100 (not leap year due to every 100 rule)
  assertEqual(LocalDate::kSunday,
      LocalDate::forComponents(2100, 2, 28).dayOfWeek());
  assertEqual(LocalDate::kMonday,
      LocalDate::forComponents(2100, 3, 1).dayOfWeek());
}

test(LocalDateTest, toAndFromEpochDays) {
  LocalDate ld;

  // Smallest LocalDate in an 8-bit implementation
  ld = LocalDate::forComponents(1872, 1, 1);
  assertEqual((acetime_t) -46751, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(-46751));

  ld = LocalDate::forComponents(1900, 1, 1);
  assertEqual((acetime_t) -36524, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(-36524));

  // Smallest date using int32_t from AceTime epoch
  ld = LocalDate::forComponents(1931, 12, 14);
  assertEqual((acetime_t) -24855, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(-24855));

  // AceTime Epoch
  ld = LocalDate::forComponents(2000, 1, 1);
  assertEqual((acetime_t) 0, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(0));

  ld = LocalDate::forComponents(2000, 2, 29);
  assertEqual((acetime_t) 59, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(59));

  ld = LocalDate::forComponents(2018, 1, 1);
  assertEqual((acetime_t) 6575, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(6575));

  // Largest date using int32_t from AceTimeEpoch
  ld = LocalDate::forComponents(2068, 1, 19);
  assertEqual((acetime_t) 24855, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(24855));

  // Largest LocalDate in an 8-bit implementation
  ld = LocalDate::forComponents(2127, 12, 31);
  assertEqual((acetime_t) 46750, ld.toEpochDays());
  assertTrue(ld == LocalDate::forEpochDays(46750));
}

// Same as toAndFromEpochDays, shifted 30 years
test(LocalDateTest, toAndFromUnixDays) {
  LocalDate ld;

  // Smallest LocalDate in an 8-bit implementation
  ld = LocalDate::forComponents(1872, 1, 1);
  assertEqual((acetime_t) -35794, ld.toUnixDays());
  assertTrue(ld == LocalDate::forUnixDays(-35794));

  // Smallest date using int32_t from Unix epoch
  ld = LocalDate::forComponents(1901, 12, 14);
  assertEqual((acetime_t) -24855, ld.toUnixDays());
  assertTrue(ld == LocalDate::forUnixDays(-24855));

  // Unix Epoch
  ld = LocalDate::forComponents(1970, 1, 1);
  assertEqual((acetime_t) 0, ld.toUnixDays());
  assertTrue(ld == LocalDate::forUnixDays(0));

  // 1970 is not a leap year, whereas 2000 is a leap year
  ld = LocalDate::forComponents(1970, 2, 28);
  assertEqual((acetime_t) 58, ld.toUnixDays());
  assertTrue(ld == LocalDate::forUnixDays(58));

  ld = LocalDate::forComponents(1988, 1, 1);
  assertEqual((acetime_t) 6574, ld.toUnixDays());
  assertTrue(ld == LocalDate::forUnixDays(6574));

  // Largest date using int32_t from Unix epoch
  ld = LocalDate::forComponents(2038, 1, 19);
  assertEqual((acetime_t) 24855, ld.toUnixDays());
  assertTrue(ld == LocalDate::forUnixDays(24855));

  // Largest LocalDate in an 8-bit implementation
  ld = LocalDate::forComponents(2127, 12, 31);
  assertEqual((acetime_t) 57707, ld.toUnixDays());
  assertTrue(ld == LocalDate::forUnixDays(57707));
}

test(LocalDateTest, toAndFromEpochSeconds) {
  LocalDate ld;

  // The smallest whole day that can be represented with an int32_t from
  // AceTime Epoch is 1931-12-14.
  ld = LocalDate::forComponents(1931, 12, 14);
  assertEqual((acetime_t) -24855 * 86400, ld.toEpochSeconds());
  assertTrue(ld == LocalDate::forEpochSeconds((acetime_t) -24855 * 86400 + 60));

  // Smallest date with an int32_t is 1931-12-13 20:45:52. The
  // forEpochSeconds() will correctly truncate the partial day *down* towards
  // the to the nearest whole day.
  ld = LocalDate::forComponents(1931, 12, 13);
  assertTrue(ld == LocalDate::forEpochSeconds(INT32_MIN + 1));

  ld = LocalDate::forComponents(2000, 1, 1);
  assertEqual((acetime_t) 0, ld.toEpochSeconds());
  assertTrue(ld == LocalDate::forEpochSeconds(0));

  ld = LocalDate::forComponents(2000, 2, 29);
  assertEqual((acetime_t) 59 * 86400, ld.toEpochSeconds());
  assertTrue(ld == LocalDate::forEpochSeconds((acetime_t) 59 * 86400 + 1));

  ld = LocalDate::forComponents(2018, 1, 1);
  assertEqual((acetime_t) 6575 * 86400, ld.toEpochSeconds());
  assertTrue(ld == LocalDate::forEpochSeconds((acetime_t) 6575 * 86400 + 2));

  // Largest date possible using AceTime Epoch Seconds is 2068-01-19 03:14:07.
  ld = LocalDate::forComponents(2068, 1, 19);
  assertEqual((acetime_t) 24855 * 86400, ld.toEpochSeconds());
  // 2068-01-19 03:14:06 (largest date at INT32_MAX - 1)
  assertTrue(ld == LocalDate::forEpochSeconds(
      (acetime_t) 24855 * 86400 + 11646));
}

test(LocalDateTest, toAndFromUnixSeconds) {
  LocalDate ld;

  // The smallest whole day that can be represented with an int32_t from AceTime
  // epoch is 1931-12-14, can't do better with unixSeconds since it uses
  // the Acetime seconds internally.
  ld = LocalDate::forComponents(1931, 12, 14);
  assertEqual((acetime_t) -13898 * 86400, ld.toUnixSeconds());
  assertTrue(ld == LocalDate::forUnixSeconds((acetime_t) -13898 * 86400 + 60));

  ld = LocalDate::forComponents(1970, 1, 1);
  assertEqual((acetime_t) 0, ld.toUnixSeconds());
  assertTrue(ld == LocalDate::forUnixSeconds(0));

  ld = LocalDate::forComponents(1970, 2, 28);
  assertEqual((acetime_t) 58 * 86400, ld.toUnixSeconds());
  assertTrue(ld == LocalDate::forUnixSeconds((acetime_t) 58 * 86400 + 1));

  ld = LocalDate::forComponents(1988, 1, 1);
  assertEqual((acetime_t) 6574 * 86400, ld.toUnixSeconds());
  assertTrue(ld == LocalDate::forUnixSeconds((acetime_t) 6574 * 86400 + 2));

  // Largest date possible using Unix Seconds is 2038-01-19 03:14:07.
  // Which means 2038-01-19 03:14:06 corresponds to INT32_MAX - 1.
  ld = LocalDate::forComponents(2038, 1, 19);
  assertEqual((acetime_t) 24855 * 86400, ld.toUnixSeconds());
  assertTrue(ld == LocalDate::forUnixSeconds((acetime_t) (INT32_MAX - 1)));
}

test(LocalDateTest, compareTo) {
  LocalDate a, b;

  a = LocalDate::forComponents(2000, 1, 1);
  b = LocalDate::forComponents(2000, 1, 1);
  assertEqual(a.compareTo(b), 0);
  assertTrue(a == b);
  assertFalse(a != b);

  a = LocalDate::forComponents(2000, 1, 1);
  b = LocalDate::forComponents(2000, 1, 2);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalDate::forComponents(2000, 1, 1);
  b = LocalDate::forComponents(2000, 2, 1);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalDate::forComponents(2000, 1, 1);
  b = LocalDate::forComponents(2001, 1, 1);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);
}

test(LocalDateTest, forDateString) {
  LocalDate ld;
  ld = LocalDate::forDateString("2000-01-01");
  assertTrue(ld == LocalDate::forComponents(2000, 1, 1));

  ld = LocalDate::forDateString("2099-02-28");
  assertTrue(ld == LocalDate::forComponents(2099, 2, 28));

  ld = LocalDate::forDateString("2127-12-31");
  assertTrue(ld == LocalDate::forComponents(2127, 12, 31));
}

test(LocalDateTest, forDateString_invalid) {
  LocalDate ld = LocalDate::forDateString("2000-01");
  assertTrue(ld.isError());
}

test(LocalDateTest, isLeapYear) {
  assertFalse(LocalDate::isLeapYear(1900));
  assertTrue(LocalDate::isLeapYear(2000));
  assertFalse(LocalDate::isLeapYear(2001));
  assertTrue(LocalDate::isLeapYear(2004));
  assertFalse(LocalDate::isLeapYear(2100));
}

test(LocalDateTest, daysInMonth) {
  assertEqual(31, LocalDate::daysInMonth(2000, 1));
  assertEqual(29, LocalDate::daysInMonth(2000, 2));
  assertEqual(31, LocalDate::daysInMonth(2000, 3));
  assertEqual(30, LocalDate::daysInMonth(2000, 4));
  assertEqual(31, LocalDate::daysInMonth(2000, 5));
  assertEqual(30, LocalDate::daysInMonth(2000, 6));
  assertEqual(31, LocalDate::daysInMonth(2000, 7));
  assertEqual(31, LocalDate::daysInMonth(2000, 8));
  assertEqual(30, LocalDate::daysInMonth(2000, 9));
  assertEqual(31, LocalDate::daysInMonth(2000, 10));
  assertEqual(30, LocalDate::daysInMonth(2000, 11));
  assertEqual(31, LocalDate::daysInMonth(2000, 12));

  assertEqual(28, LocalDate::daysInMonth(2001, 2));
  assertEqual(29, LocalDate::daysInMonth(2004, 2));
  assertEqual(28, LocalDate::daysInMonth(2100, 2));
}

test(LocalDateTest, incrementOneDay) {
  LocalDate ld;

  ld = LocalDate::forComponents(2000, 2, 28);
  local_date_mutation::incrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2000, 2, 29));

  ld = LocalDate::forComponents(2000, 2, 29);
  local_date_mutation::incrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2000, 3, 1));

  ld = LocalDate::forComponents(2000, 3, 31);
  local_date_mutation::incrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2000, 4, 1));

  ld = LocalDate::forComponents(2000, 12, 31);
  local_date_mutation::incrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2001, 1, 1));

  ld = LocalDate::forComponents(2001, 2, 28);
  local_date_mutation::incrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2001, 3, 1));

  ld = LocalDate::forComponents(2004, 2, 28);
  local_date_mutation::incrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2004, 2, 29));
}

test(LocalDateTest, decrementOneDay) {
  LocalDate ld;

  ld = LocalDate::forComponents(2004, 2, 29);
  local_date_mutation::decrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2004, 2, 28));

  ld = LocalDate::forComponents(2001, 3, 1);
  local_date_mutation::decrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2001, 2, 28));

  ld = LocalDate::forComponents(2001, 1, 1);
  local_date_mutation::decrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2000, 12, 31));

  ld = LocalDate::forComponents(2000, 4, 1);
  local_date_mutation::decrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2000, 3, 31));

  ld = LocalDate::forComponents(2000, 3, 1);
  local_date_mutation::decrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2000, 2, 29));

  ld = LocalDate::forComponents(2000, 2, 29);
  local_date_mutation::decrementOneDay(ld);
  assertTrue(ld == LocalDate::forComponents(2000, 2, 28));
}

// --------------------------------------------------------------------------
// LocalTime
// --------------------------------------------------------------------------

test(LocalTimeTest, accessors) {
  LocalTime lt = LocalTime::forComponents(1, 2, 3);
  assertEqual(1, lt.hour());
  assertEqual(2, lt.minute());
  assertEqual(3, lt.second());
}

test(LocalTimeTest, isError) {
  assertFalse(LocalTime::forComponents(0, 0, 0).isError());
  assertFalse(LocalTime::forComponents(0, 59, 0).isError());
  assertFalse(LocalTime::forComponents(0, 59, 59).isError());
  assertFalse(LocalTime::forComponents(23, 59, 59).isError());
  assertFalse(LocalTime::forComponents(24, 0, 0).isError());

  assertTrue(LocalTime::forComponents(24, 0, 1).isError());
  assertTrue(LocalTime::forComponents(25, 0, 0).isError());
  assertTrue(LocalTime::forComponents(0, 60, 0).isError());
  assertTrue(LocalTime::forComponents(0, 0, 60).isError());
}

test(LocalTimeTest, forError) {
  LocalTime lt = LocalTime::forError();
  assertTrue(lt.isError());
  assertEqual(LocalTime::kInvalidSeconds, lt.toSeconds());

  lt = LocalTime::forSeconds(LocalTime::kInvalidSeconds);
  assertTrue(lt.isError());
}

test(LocalTimeTest, toAndFromSeconds) {
  LocalTime lt;

  lt = LocalTime::forSeconds(0);
  assertTrue(lt == LocalTime::forComponents(0, 0, 0));
  assertEqual((acetime_t) 0, lt.toSeconds());

  lt = LocalTime::forSeconds(3662);
  assertTrue(lt == LocalTime::forComponents(1, 1, 2));
  assertEqual((acetime_t) 3662, lt.toSeconds());

  lt = LocalTime::forSeconds(86399);
  assertTrue(lt == LocalTime::forComponents(23, 59, 59));
  assertEqual((acetime_t) 86399, lt.toSeconds());
}

test(LocalTimeTest, compareTo) {
  LocalTime a, b;

  a = LocalTime::forComponents(0, 1, 1);
  b = LocalTime::forComponents(0, 1, 1);
  assertEqual(a.compareTo(b), 0);
  assertTrue(a == b);
  assertFalse(a != b);

  a = LocalTime::forComponents(0, 1, 1);
  b = LocalTime::forComponents(0, 1, 2);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalTime::forComponents(0, 1, 1);
  b = LocalTime::forComponents(0, 2, 1);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalTime::forComponents(0, 1, 1);
  b = LocalTime::forComponents(1, 1, 1);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);
}

test(LocalTimeTest, forTimeString) {
  LocalTime lt;
  lt = LocalTime::forTimeString("00:00:00");
  assertTrue(lt == LocalTime::forComponents(0, 0, 0));

  lt = LocalTime::forTimeString("01:02:03");
  assertTrue(lt == LocalTime::forComponents(1, 2, 3));
}

test(LocalTimeTest, fortimeString_invalid) {
  LocalTime lt = LocalTime::forTimeString("01:02");
  assertTrue(lt.isError());
}

// --------------------------------------------------------------------------
// LocalDateTime
// --------------------------------------------------------------------------

test(LocalDateTimeTest, accessors) {
  LocalDateTime dt = LocalDateTime::forComponents(2001, 2, 3, 4, 5, 6);
  assertEqual((int16_t) 2001, dt.year());
  assertEqual(1, dt.yearTiny());
  assertEqual(2, dt.month());
  assertEqual(3, dt.day());
  assertEqual(4, dt.hour());
  assertEqual(5, dt.minute());
  assertEqual(6, dt.second());
}

test(LocalDateTimeTest, invalidSeconds) {
  LocalDateTime dt = LocalDateTime::forEpochSeconds(
      LocalDate::kInvalidEpochSeconds);
  assertTrue(dt.isError());
  assertEqual(LocalDate::kInvalidEpochSeconds, dt.toEpochSeconds());
  assertEqual(LocalDate::kInvalidEpochDays, dt.toEpochDays());
}

test(LocalDateTimeTest, forError) {
  LocalDateTime dt = LocalDateTime::forError();
  assertTrue(dt.isError());
}

test(LocalDateTimeTest, isError) {
  // 2018-01-01 00:00:00Z
  LocalDateTime dt = LocalDateTime::forComponents(2018, 1, 1, 0, 0, 0);
  assertFalse(dt.isError());

  dt = LocalDateTime::forComponents(2018, 0, 1, 0, 0, 0);
  assertTrue(dt.isError());

  dt = LocalDateTime::forComponents(2018, 255, 1, 0, 0, 0);
  assertTrue(dt.isError());

  dt = LocalDateTime::forComponents(2018, 1, 0, 0, 0, 0);
  assertTrue(dt.isError());

  dt = LocalDateTime::forComponents(2018, 1, 255, 0, 0, 0);
  assertTrue(dt.isError());

  dt = LocalDateTime::forComponents(2018, 1, 1, 255, 0, 0);
  assertTrue(dt.isError());

  dt = LocalDateTime::forComponents(2018, 1, 1, 0, 255, 0);
  assertTrue(dt.isError());

  dt = LocalDateTime::forComponents(2018, 1, 1, 0, 0, 255);
  assertTrue(dt.isError());
}

test(LocalDateTimeTest, forComponents) {
  LocalDateTime dt;

  // 1931-12-13 20:45:52Z, smalltest datetime using int32_t from AceTime Epoch.
  // Let's use +1 of that since INT_MIN will be used to indicate an error.
  dt = LocalDateTime::forComponents(1931, 12, 13, 20, 45, 53);
  assertEqual((acetime_t) -24856, dt.toEpochDays());
  assertEqual((acetime_t) -13899, dt.toUnixDays());
  assertEqual((acetime_t) (INT32_MIN + 1), dt.toEpochSeconds());
  assertEqual(LocalDate::kSunday, dt.dayOfWeek());

  // 2000-01-01 00:00:00Z Saturday
  dt = LocalDateTime::forComponents(2000, 1, 1, 0, 0, 0);
  assertEqual((acetime_t) 0, dt.toEpochDays());
  assertEqual((acetime_t) 10957, dt.toUnixDays());
  assertEqual((acetime_t) 0, dt.toEpochSeconds());
  assertEqual(LocalDate::kSaturday, dt.dayOfWeek());

  // 2000-01-02 00:00:00Z Sunday
  dt = LocalDateTime::forComponents(2000, 1, 2, 0, 0, 0);
  assertEqual((acetime_t) 1, dt.toEpochDays());
  assertEqual((acetime_t) 10958, dt.toUnixDays());
  assertEqual((acetime_t) 86400, dt.toEpochSeconds());
  assertEqual(LocalDate::kSunday, dt.dayOfWeek());

  // 2000-02-29 00:00:00Z Tuesday
  dt = LocalDateTime::forComponents(2000, 2, 29, 0, 0, 0);
  assertEqual((acetime_t) 59, dt.toEpochDays());
  assertEqual((acetime_t) 11016, dt.toUnixDays());
  assertEqual((acetime_t) 86400 * 59, dt.toEpochSeconds());
  assertEqual(LocalDate::kTuesday, dt.dayOfWeek());

  // 2018-01-01 00:00:00Z Monday
  dt = LocalDateTime::forComponents(2018, 1, 1, 0, 0, 0);
  assertEqual((acetime_t) 6575, dt.toEpochDays());
  assertEqual((acetime_t) 17532, dt.toUnixDays());
  assertEqual(6575 * (acetime_t) 86400, dt.toEpochSeconds());
  assertEqual(LocalDate::kMonday, dt.dayOfWeek());

  // 2038-01-19 03:14:07Z (largest value using Unix Epoch)
  dt = LocalDateTime::forComponents(2038, 1, 19, 3, 14, 7);
  assertEqual((acetime_t) 13898, dt.toEpochDays());
  assertEqual((acetime_t) 24855, dt.toUnixDays());
  assertEqual((acetime_t) 1200798847, dt.toEpochSeconds());
  assertEqual(LocalDate::kTuesday, dt.dayOfWeek());

  // 2068-01-19 03:14:06Z (largest value for AceTime Epoch).
  // INT32_MAX is used as a sentinel invalid value.
  // TODO: Change this to INT32_MIN.
  dt = LocalDateTime::forComponents(2068, 1, 19, 3, 14, 6);
  assertEqual((acetime_t) 24855, dt.toEpochDays());
  assertEqual((acetime_t) 35812, dt.toUnixDays());
  assertEqual((acetime_t) (INT32_MAX - 1), dt.toEpochSeconds());
  assertEqual(LocalDate::kThursday, dt.dayOfWeek());
}

test(LocalDateTimeTest, toAndForUnixSeconds) {
  LocalDateTime dt;
  LocalDateTime udt;

  // 1931-12-13 20:45:52Z, smalltest datetime using int32_t from AceTime Epoch.
  // Let's use +1 of that since INT_MIN will be used to indicate an error.
  dt = LocalDateTime::forComponents(1931, 12, 13, 20, 45, 53);
  assertEqual((acetime_t) -1200798847, dt.toUnixSeconds());
  udt = LocalDateTime::forUnixSeconds(dt.toUnixSeconds());
  assertTrue(dt == udt);

  // 1970-01-01 00:00:00Z
  dt = LocalDateTime::forComponents(1970, 1, 1, 0, 0, 0);
  assertEqual((acetime_t) 0, dt.toUnixSeconds());
  udt = LocalDateTime::forUnixSeconds(dt.toUnixSeconds());
  assertTrue(dt == udt);

  // 2000-01-01 00:00:00Z
  dt = LocalDateTime::forComponents(2000, 1, 1, 0, 0, 0);
  assertEqual((acetime_t) 946684800, dt.toUnixSeconds());
  udt = LocalDateTime::forUnixSeconds(dt.toUnixSeconds());
  assertTrue(dt == udt);

  // 2018-01-01 00:00:00Z
  dt = LocalDateTime::forComponents(2018, 1, 1, 0, 0, 0);
  assertEqual((acetime_t) 1514764800, dt.toUnixSeconds());
  udt = LocalDateTime::forUnixSeconds(dt.toUnixSeconds());
  assertTrue(dt == udt);

  // 2038-01-19 03:14:06Z (largest value - 1 using Unix Epoch)
  dt = LocalDateTime::forComponents(2038, 1, 19, 3, 14, 6);
  assertEqual((acetime_t) (INT32_MAX - 1), dt.toUnixSeconds());
  udt = LocalDateTime::forUnixSeconds(dt.toUnixSeconds());
  assertTrue(dt == udt);
}

test(LocalDateTimeTest, forEpochSeconds) {
  // 2029-12-31 23:59:59Z Monday
  LocalDateTime dt = LocalDateTime::forEpochSeconds(
      10958 * (acetime_t) 86400 - 1);

  assertEqual((int16_t) 2029, dt.year());
  assertEqual(29, dt.yearTiny());
  assertEqual(12, dt.month());
  assertEqual(31, dt.day());
  assertEqual(23, dt.hour());
  assertEqual(59, dt.minute());
  assertEqual(59, dt.second());
  assertEqual(LocalDate::kMonday, dt.dayOfWeek());
}

test(LocalDateTimeTest, compareTo) {
  LocalDateTime a = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 0);
  LocalDateTime b = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 0);
  assertEqual(a.compareTo(b), 0);
  assertTrue(a == b);
  assertFalse(a != b);

  a = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 0);
  b = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 1);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 0);
  b = LocalDateTime::forComponents(2018, 1, 1, 12, 1, 0);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 0);
  b = LocalDateTime::forComponents(2018, 1, 2, 12, 0, 0);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 0);
  b = LocalDateTime::forComponents(2018, 2, 1, 12, 0, 0);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);

  a = LocalDateTime::forComponents(2018, 1, 1, 12, 0, 0);
  b = LocalDateTime::forComponents(2019, 1, 1, 12, 0, 0);
  assertLess(a.compareTo(b), 0);
  assertMore(b.compareTo(a), 0);
  assertTrue(a != b);
}

test(LocalDateTimeTest, dayOfWeek) {
  // 2018-01-01 00:00:00Z Monday
  LocalDateTime dt = LocalDateTime::forComponents(2018, 1, 1, 0, 0, 0);
  assertEqual(LocalDate::kMonday, dt.dayOfWeek());

  dt.hour(23); // 2018-01-01 23:00:00Z, no change to dayOfWeek
  assertEqual(LocalDate::kMonday, dt.dayOfWeek());

  dt.minute(40); // 2018-01-01 23:40:00Z, no change to dayOfWeek
  assertEqual(LocalDate::kMonday, dt.dayOfWeek());

  dt.second(3); // 2018-01-01 23:40:03Z, no change to dayOfWeek
  assertEqual(LocalDate::kMonday, dt.dayOfWeek());

  dt.day(2); // 2018-01-02 23:40:03+00:45, changes dayOfWeek
  assertEqual(LocalDate::kTuesday, dt.dayOfWeek());

  dt.month(2); // 2018-02-02 23:40:03+00:45, changes dayOfWeek
  assertEqual(LocalDate::kFriday, dt.dayOfWeek());

  dt.yearTiny(19); // 2019-02-02 23:40:03+00:45, changes dayOfWeek
  assertEqual(LocalDate::kSaturday, dt.dayOfWeek());

  dt.year(2020); // 2020-02-02 23:40:03+00:45, changes dayOfWeek
  assertEqual(LocalDate::kSunday, dt.dayOfWeek());
}

test(LocalDateTimeTest, forDateString) {
  // exact ISO8601 format
  LocalDateTime dt = LocalDateTime::forDateString(F("2018-08-31T13:48:01"));
  assertFalse(dt.isError());
  assertEqual((int16_t) 2018, dt.year());
  assertEqual(18, dt.yearTiny());
  assertEqual(8, dt.month());
  assertEqual(31, dt.day());
  assertEqual(13, dt.hour());
  assertEqual(48, dt.minute());
  assertEqual(1, dt.second());
  assertEqual(LocalDate::kFriday, dt.dayOfWeek());

  // parser does not care about most separators, this may change in the future
  dt = LocalDateTime::forDateString(F("2018/08/31 13#48#01"));
  assertFalse(dt.isError());
  assertEqual((int16_t) 2018, dt.year());
  assertEqual(18, dt.yearTiny());
  assertEqual(8, dt.month());
  assertEqual(31, dt.day());
  assertEqual(13, dt.hour());
  assertEqual(48, dt.minute());
  assertEqual(1, dt.second());
  assertEqual(LocalDate::kFriday, dt.dayOfWeek());
}

test(LocalDateTimeTest, forDateString_errors) {
  // empty string, too short
  LocalDateTime dt = LocalDateTime::forDateString("");
  assertTrue(dt.isError());

  // not enough components
  dt = LocalDateTime::forDateString(F("2018-08-31"));
  assertTrue(dt.isError());

  // too long
  dt = LocalDateTime::forDateString(F("2018-08-31T13:48:01-07:00"));
  assertTrue(dt.isError());

  // too short
  dt = LocalDateTime::forDateString(F("2018-08-31T13:48"));
  assertTrue(dt.isError());
}

// --------------------------------------------------------------------------

void setup() {
#if !defined(__linux__) && !defined(__APPLE__)
  delay(1000); // wait for stability on some boards to prevent garbage Serial
#endif
  Serial.begin(115200); // ESP8266 default of 74880 not supported on Linux
  while(!Serial); // for the Arduino Leonardo/Micro only
}

void loop() {
  TestRunner::run();
}
