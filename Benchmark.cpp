#include <stdint.h>
#include <Arduino.h>
#include <AceTime.h>
#include "Benchmark.h"

using namespace ace_time;

#if defined(AVR)
const uint32_t COUNT = 10000;
#elif defined(ESP8266)
const uint32_t COUNT = 50000;
#else
const uint32_t COUNT = 200000;
#endif

const uint32_t MILLIS_TO_NANO_PER_ITERATION = ( 1000000 / COUNT);

const char TOP[] = 
  "----------------------------+---------+";
const char HEADER[] = 
  "Method                      |  micros |";
const char DIVIDER[] = 
  "----------------------------|---------|";
const char BOTTOM[] = 
  "----------------------------+---------+";
const char EMPTY_LOOP_LABEL[] =
  "Empty loop                  | ";
const char CONSTRUCTOR1_LABEL[] =
  "DateTime(y,m,d,h,m,s)       | ";
const char CONSTRUCTOR2_LABEL[] =
  "DateTime(seconds)           | ";
const char DAYS_SINCE_EPOCH_LABEL[] =
  "toDaysSinceEpochMillis()    | ";
const char SECOND_SINCE_EPOCH_LABEL[] =
  "toSecondsSinceEpochMillis() | ";
const char ENDING[] = " |";

// The compiler is extremelly good about removing code that does nothing. This
// variable is used to ensure user-visible side-effects, preventing the compiler
// optimization.
uint32_t guard;
void disableOptimization(const DateTime& dt) {
  guard ^= ((uint32_t) dt.year() << 24)
         ^ ((uint32_t) dt.month() << 16)
         ^ ((uint32_t) dt.day() << 8)
         ^ ((uint32_t) dt.hour() << 16)
         ^ ((uint32_t) dt.minute() << 8)
         ^ ((uint32_t) dt.second())
         ^ dt.timeZone().tzCode();
}

// A small helper that runs the given lamba expression in a loop
// and returns how long it took.
template <typename F>
unsigned long runLambda(uint32_t count, F&& lambda) {
  unsigned long startMillis = millis();
  while (count--) {
    lambda();
  }
  return millis() - startMillis;
}

void printPad3(uint16_t val, char padChar) {
  if (val < 100) Serial.print(padChar);
  if (val < 10) Serial.print(padChar);
  Serial.print(val);
}

/**
 * Given total elapsed time in millis, print micros per iteration as
 * a floating point number (without using floating point operations).
 */
void printMicrosPerIteration(unsigned long elapsedMillis) {
  unsigned long nanos = elapsedMillis * MILLIS_TO_NANO_PER_ITERATION;
  uint16_t whole = nanos / 1000;
  uint16_t frac = nanos % 1000;
  printPad3(whole, ' ');
  Serial.print('.');
  printPad3(frac, '0');
}

void runBenchmark() {
  Serial.println(TOP);
  Serial.println(HEADER);
  Serial.println(DIVIDER);

  // Empty loop
  unsigned long emptyLoopMillis = runLambda(COUNT, []() {
    unsigned long tickMillis = millis();
    guard ^= tickMillis;
    digitalWrite(LED_BENCHMARK, guard);
  });
  yield();
  Serial.print(EMPTY_LOOP_LABEL);
  printMicrosPerIteration(emptyLoopMillis);
  Serial.println(ENDING);
  Serial.println(DIVIDER);

  // DateTime(seconds) constructor
  unsigned long constructorFromSecondsMillis =
      runLambda(COUNT, []() mutable {
    unsigned long tickMillis = millis();
    // DateTime(seconds) takes seconds, but use millis for testing purposes.
    DateTime dateTime = DateTime(tickMillis);

    disableOptimization(dateTime);
    digitalWrite(LED_BENCHMARK, guard);
  });
  yield();
  Serial.print(CONSTRUCTOR2_LABEL);
  printMicrosPerIteration(constructorFromSecondsMillis - emptyLoopMillis);
  Serial.println(ENDING);

  // DateTime::toDaysSinceEpoch()
  unsigned long toDaysSinceEpochMillis = runLambda(COUNT, []() mutable {
    unsigned long tickMillis = millis();
    // DateTime(seconds) takes seconds, but use millis for testing purposes.
    DateTime dateTime = DateTime(tickMillis);
    uint32_t daysSinceEpoch = dateTime.toDaysSinceEpoch();

    guard ^= daysSinceEpoch;
    disableOptimization(dateTime);
    digitalWrite(LED_BENCHMARK, guard);
  });
  yield();
  Serial.print(DAYS_SINCE_EPOCH_LABEL);
  printMicrosPerIteration(
      toDaysSinceEpochMillis - constructorFromSecondsMillis);
  Serial.println(ENDING);

  // DateTime::toSecondsSinceEpoch()
  unsigned long toSecondsSinceEpochMillis = runLambda(COUNT, []() mutable {
    unsigned long tickMillis = millis();
    // DateTime(seconds) takes seconds, but use millis for testing purposes.
    DateTime dateTime = DateTime(tickMillis);
    uint32_t secondsSinceEpoch = dateTime.toSecondsSinceEpoch();

    guard ^= secondsSinceEpoch;
    disableOptimization(dateTime);
    digitalWrite(LED_BENCHMARK, guard);
  });
  yield();
  Serial.print(SECOND_SINCE_EPOCH_LABEL);
  printMicrosPerIteration(
      toSecondsSinceEpochMillis - constructorFromSecondsMillis);
  Serial.println(ENDING);

  Serial.println(BOTTOM);

  // Print some stats
  Serial.print("Number of iterations per run: ");
  Serial.println(COUNT);
}
