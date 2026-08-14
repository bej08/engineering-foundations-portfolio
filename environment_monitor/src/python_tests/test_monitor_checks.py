"""
test_monitor_checks.py

Unit tests for the reading validation logic. These require no hardware and
run anywhere, which is deliberate: the point of separating parsing and
validation from serial I/O is that the logic can be tested without a device
attached.

Covers TEST_PLAN.md cases TC-02 (photoresistor range), TC-07 (DHT11 output
validity) and TC-08 (combined output format).
"""

import pytest

from monitor_checks import (
    ReadingError,
    is_valid,
    parse_reading,
    validate_reading,
)

VALID_LINE = '{"time":"14:32:07","temp":23,"hum":45,"light":512,"fan":0}'


# --- parse_reading ----------------------------------------------------------


def test_parses_a_well_formed_line():
    reading = parse_reading(VALID_LINE)
    assert reading["temp"] == 23
    assert reading["hum"] == 45
    assert reading["light"] == 512
    assert reading["time"] == "14:32:07"


def test_ignores_surrounding_whitespace():
    reading = parse_reading("  " + VALID_LINE + "\r\n")
    assert reading["temp"] == 23


@pytest.mark.parametrize(
    "line, reason",
    [
        ("", "empty line"),
        ("   ", "whitespace only"),
        (None, "no line at all"),
        ("not json", "plain text"),
        ('{"time":"14:32:07","temp":23', "truncated mid-line"),
        ("[1, 2, 3]", "JSON array rather than object"),
    ],
)
def test_rejects_unusable_lines(line, reason):
    """
    Truncated lines are the important case here. The Arduino resets when the
    serial port opens, so a partial first line is normal and must raise a
    handled error rather than crash the reader.
    """
    with pytest.raises(ReadingError):
        parse_reading(line)


def test_rejects_line_missing_a_required_field():
    line = '{"time":"14:32:07","temp":23,"hum":45}'  # no light
    with pytest.raises(ReadingError) as exc:
        parse_reading(line)
    assert "light" in str(exc.value)


# --- validate_reading -------------------------------------------------------


def test_plausible_reading_has_no_problems():
    assert validate_reading(parse_reading(VALID_LINE)) == []


@pytest.mark.parametrize("temp", [0, 25, 50])
def test_temperatures_within_datasheet_range_are_accepted(temp):
    """0 C and 50 C are the DHT11's stated limits, so both must pass."""
    reading = {"time": "12:00:00", "temp": temp, "hum": 50, "light": 500}
    assert validate_reading(reading) == []


@pytest.mark.parametrize("temp", [-1, 51, -40, 200])
def test_temperatures_outside_datasheet_range_are_flagged(temp):
    reading = {"time": "12:00:00", "temp": temp, "hum": 50, "light": 500}
    problems = validate_reading(reading)
    assert any("temperature" in p for p in problems)


@pytest.mark.parametrize("humidity", [20, 55, 90])
def test_humidity_within_range_is_accepted(humidity):
    reading = {"time": "12:00:00", "temp": 20, "hum": humidity, "light": 500}
    assert validate_reading(reading) == []


@pytest.mark.parametrize("humidity", [19, 91, -5, 150])
def test_humidity_outside_range_is_flagged(humidity):
    reading = {"time": "12:00:00", "temp": 20, "hum": humidity, "light": 500}
    problems = validate_reading(reading)
    assert any("humidity" in p for p in problems)


@pytest.mark.parametrize("light", [0, 512, 1023])
def test_light_within_adc_range_is_accepted(light):
    """0 and 1023 are the limits of the 10-bit ADC, so both are legitimate."""
    reading = {"time": "12:00:00", "temp": 20, "hum": 50, "light": light}
    assert validate_reading(reading) == []


@pytest.mark.parametrize("light", [-1, 1024, 9999])
def test_light_outside_adc_range_is_flagged(light):
    """
    An analogRead result cannot exceed 1023 on this hardware, so a value
    outside that range indicates corruption rather than an unusual condition.
    """
    reading = {"time": "12:00:00", "temp": 20, "hum": 50, "light": light}
    problems = validate_reading(reading)
    assert any("light" in p for p in problems)


@pytest.mark.parametrize(
    "timestamp",
    ["24:00:00", "12:60:00", "12:00:60", "12:00", "noon", "", "1:2"],
)
def test_malformed_timestamps_are_flagged(timestamp):
    reading = {"time": timestamp, "temp": 20, "hum": 50, "light": 500}
    problems = validate_reading(reading)
    assert any("timestamp" in p for p in problems)


def test_multiple_faults_are_all_reported():
    """
    A sensor failing badly can corrupt several fields at once, so validation
    returns every problem rather than stopping at the first.
    """
    reading = {"time": "99:99:99", "temp": 200, "hum": -5, "light": 5000}
    problems = validate_reading(reading)
    assert len(problems) == 4


def test_non_integer_values_are_flagged_not_crashed():
    """Guards against a TypeError if the sketch ever emits strings."""
    reading = {"time": "12:00:00", "temp": "23", "hum": None, "light": 4.5}
    problems = validate_reading(reading)
    assert len(problems) == 3


# --- is_valid ---------------------------------------------------------------


def test_is_valid_accepts_a_good_line():
    assert is_valid(VALID_LINE) is True


@pytest.mark.parametrize(
    "line",
    [
        "",
        "garbage",
        '{"time":"14:32:07","temp":900,"hum":45,"light":512}',
    ],
)
def test_is_valid_rejects_bad_lines(line):
    assert is_valid(line) is False
