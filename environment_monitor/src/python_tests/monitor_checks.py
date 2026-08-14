"""
monitor_checks.py

Validation logic for readings produced by the OT Environment Monitor.

Kept separate from the tests themselves so it can be imported by both the
test suite and, later, the supervisory service. Sensor bounds come from the
component datasheets rather than being chosen arbitrarily, so a reading
outside them indicates a genuine fault (or manipulation) rather than simply
an unusual environment.
"""

import json

# Bounds taken from the DHT11 datasheet: 0-50 C and 20-90 % RH.
# A reading outside these is not merely unusual, it is outside what the
# sensor is physically specified to report, so it indicates a fault.
TEMP_MIN_C = 0
TEMP_MAX_C = 50
HUMIDITY_MIN_PCT = 20
HUMIDITY_MAX_PCT = 90

# The photoresistor is read by a 10-bit ADC, so the range is fixed by the
# hardware and cannot legitimately be exceeded.
LIGHT_MIN = 0
LIGHT_MAX = 1023

REQUIRED_FIELDS = ("time", "temp", "hum", "light")


class ReadingError(ValueError):
    """Raised when a serial line cannot be turned into a usable reading."""


def parse_reading(line):
    """
    Turn one line of serial output into a reading dictionary.

    Raises ReadingError for anything unusable. The Arduino resets when the
    serial port is opened, so partial first lines are expected in normal
    operation and must not be treated as a crash.
    """
    if line is None:
        raise ReadingError("no line supplied")

    line = line.strip()
    if not line:
        raise ReadingError("empty line")

    try:
        reading = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ReadingError(f"not valid JSON: {exc}") from exc

    if not isinstance(reading, dict):
        raise ReadingError("expected a JSON object")

    missing = [f for f in REQUIRED_FIELDS if f not in reading]
    if missing:
        raise ReadingError(f"missing fields: {', '.join(missing)}")

    return reading


def validate_reading(reading):
    """
    Check a parsed reading against datasheet limits.

    Returns a list of problem descriptions. An empty list means the reading
    is plausible. Returning a list rather than raising means a single reading
    can report several faults at once, which matters when a sensor fails in
    a way that corrupts more than one field.
    """
    problems = []

    temp = reading.get("temp")
    if not isinstance(temp, int):
        problems.append("temperature is not an integer")
    elif not TEMP_MIN_C <= temp <= TEMP_MAX_C:
        problems.append(
            f"temperature {temp}C outside sensor range "
            f"{TEMP_MIN_C}-{TEMP_MAX_C}C"
        )

    humidity = reading.get("hum")
    if not isinstance(humidity, int):
        problems.append("humidity is not an integer")
    elif not HUMIDITY_MIN_PCT <= humidity <= HUMIDITY_MAX_PCT:
        problems.append(
            f"humidity {humidity}% outside sensor range "
            f"{HUMIDITY_MIN_PCT}-{HUMIDITY_MAX_PCT}%"
        )

    light = reading.get("light")
    if not isinstance(light, int):
        problems.append("light level is not an integer")
    elif not LIGHT_MIN <= light <= LIGHT_MAX:
        problems.append(
            f"light level {light} outside ADC range {LIGHT_MIN}-{LIGHT_MAX}"
        )

    time_str = reading.get("time")
    if not isinstance(time_str, str) or not _looks_like_time(time_str):
        problems.append(f"timestamp {time_str!r} is not in HH:MM:SS form")

    return problems


def _looks_like_time(value):
    """Check an HH:MM:SS string without pulling in a date library."""
    parts = value.split(":")
    if len(parts) != 3:
        return False
    try:
        hours, minutes, seconds = (int(p) for p in parts)
    except ValueError:
        return False
    return 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59


def is_valid(line):
    """Convenience wrapper: True if a raw line parses and passes validation."""
    try:
        reading = parse_reading(line)
    except ReadingError:
        return False
    return not validate_reading(reading)
