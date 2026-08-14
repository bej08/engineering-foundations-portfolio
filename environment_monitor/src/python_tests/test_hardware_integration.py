"""
test_hardware_integration.py

Integration tests that run against the real Arduino over USB serial.

These automate checks that were previously done by eye in the Serial Monitor
(TEST_PLAN.md TC-02, TC-07, TC-08). They skip rather than fail when no
device is connected, so the suite still runs cleanly on a machine without
the hardware.

Requires the sketch to emit newline-delimited JSON (see supervisor/SETUP.md
step 1). Close the Arduino IDE's Serial Monitor first: only one program can
hold the serial port.
"""

import time

import pytest

from monitor_checks import ReadingError, parse_reading, validate_reading

pytestmark = pytest.mark.hardware


def read_valid_readings(connection, count, timeout_s=30):
    """
    Collect `count` parseable readings, ignoring unparseable lines.

    Partial lines are expected immediately after a board reset, so they are
    skipped rather than failed. If the device is genuinely silent the timeout
    catches it.
    """
    readings = []
    deadline = time.monotonic() + timeout_s

    while len(readings) < count and time.monotonic() < deadline:
        raw = connection.readline()
        if not raw:
            continue
        line = raw.decode("utf-8", errors="replace")
        try:
            readings.append(parse_reading(line))
        except ReadingError:
            continue

    return readings


def test_device_produces_a_parseable_reading(serial_connection):
    """TC-08: the controller emits output the supervisory service can read."""
    readings = read_valid_readings(serial_connection, 1)
    assert readings, (
        "No parseable reading received within the timeout. Check the sketch "
        "is emitting JSON and the baud rate matches."
    )


def test_consecutive_readings_are_all_plausible(serial_connection):
    """
    TC-07 / TC-02: ten consecutive readings all sit within datasheet limits.

    Ten rather than one because intermittent faults are the ones that matter.
    A sensor that reads correctly once and then corrupts is exactly the
    failure mode a single manual check in the Serial Monitor would miss.
    """
    readings = read_valid_readings(serial_connection, 10)
    assert len(readings) == 10, f"only got {len(readings)} readings"

    failures = []
    for index, reading in enumerate(readings):
        problems = validate_reading(reading)
        if problems:
            failures.append(f"reading {index}: {'; '.join(problems)}")

    assert not failures, "\n".join(failures)


def test_readings_arrive_at_a_reasonable_rate(serial_connection):
    """
    The sketch emits roughly one reading per second, so five should arrive
    well inside fifteen seconds. A slower rate points at a blocking call or
    a sensor timing out and retrying.
    """
    start = time.monotonic()
    readings = read_valid_readings(serial_connection, 5, timeout_s=15)
    elapsed = time.monotonic() - start

    assert len(readings) == 5, f"only {len(readings)} readings in {elapsed:.1f}s"
    assert elapsed < 15


def test_clock_is_advancing(serial_connection):
    """
    TC-04: the DS1307 timestamp changes between readings.

    A frozen timestamp means the RTC has stopped oscillating even though it
    still responds over I2C, which would otherwise look like a working clock.
    """
    readings = read_valid_readings(serial_connection, 5)
    assert len(readings) == 5

    timestamps = [r["time"] for r in readings]
    assert len(set(timestamps)) > 1, (
        f"timestamp did not change across five readings: {timestamps[0]}"
    )


@pytest.mark.manual
def test_light_sensor_responds_to_being_covered(serial_connection):
    """
    TC-02, manual: covering the photoresistor changes the reading.

    Deselected by default since it needs someone present. Run with:
        pytest -m manual
    """
    print("\nLeave the photoresistor uncovered. Waiting 3 seconds...")
    time.sleep(3)
    uncovered = read_valid_readings(serial_connection, 3)

    print("Now COVER the photoresistor with your hand. Waiting 5 seconds...")
    time.sleep(5)
    covered = read_valid_readings(serial_connection, 3)

    uncovered_avg = sum(r["light"] for r in uncovered) / len(uncovered)
    covered_avg = sum(r["light"] for r in covered) / len(covered)

    assert covered_avg != uncovered_avg, (
        f"light reading did not change when covered "
        f"(uncovered {uncovered_avg:.0f}, covered {covered_avg:.0f})"
    )
