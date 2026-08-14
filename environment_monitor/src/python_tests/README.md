# Python Test Suite

Automated tests for the OT Environment Monitor, written with pytest.

Several checks in [TEST_PLAN.md](../TEST_PLAN.md) were originally done by eye in the Arduino IDE's Serial Monitor. That works once, but it does not catch intermittent faults and it cannot be repeated consistently. This suite automates them.

## Structure

| File | Purpose | Needs hardware |
|---|---|---|
| `monitor_checks.py` | Parsing and validation logic under test | No |
| `test_monitor_checks.py` | Unit tests for that logic | No |
| `test_hardware_integration.py` | Tests against a connected Arduino | Yes |
| `conftest.py` | Shared fixtures, including the serial connection | — |
| `pytest.ini` | Marker definitions and default options | — |

The split is deliberate. Parsing and validation are kept separate from serial I/O so they can be tested without a device attached, which means the unit tests run on any machine, in seconds, with no setup. The hardware tests skip rather than fail when no Arduino is present, so a missing device reports as "skipped" while a genuine fault reports as "failed" — two different signals that would otherwise be indistinguishable.

## Running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest                 # unit tests, plus hardware tests if a board is connected
pytest -m "not hardware"   # unit tests only
pytest -m manual           # tests needing someone to cover the sensor
```

Manual tests are excluded by default so the suite can run unattended.

Hardware tests need the sketch emitting newline-delimited JSON (see [supervisor/SETUP.md](../supervisor/SETUP.md) step 1), and the Arduino IDE's Serial Monitor closed, since only one program can hold the serial port.

## What the tests check

**Unit tests (43 cases)**

- Well-formed lines parse correctly, including with trailing whitespace
- Empty, truncated, non-JSON and wrong-type lines raise a handled error rather than crashing
- Lines missing a required field are rejected, naming the missing field
- Temperature, humidity and light values are checked against limits taken from the DHT11 datasheet (0–50 °C, 20–90 % RH) and the ADC's fixed 0–1023 range
- Boundary values are tested from both sides — 0 °C and 50 °C pass, −1 °C and 51 °C fail
- Timestamps are validated as real HH:MM:SS values, so `24:00:00` and `12:60:00` are rejected
- A badly corrupted reading reports every problem at once rather than stopping at the first
- Non-integer values are flagged rather than causing a TypeError

**Hardware integration tests**

- The controller emits at least one parseable reading (TC-08)
- Ten consecutive readings are all within datasheet limits (TC-07, TC-02)
- Readings arrive at roughly the expected rate
- The RTC timestamp advances between readings, catching a clock that responds over I2C but has stopped oscillating (TC-04)
- Manual: covering the photoresistor changes the reading (TC-02)

## Why ten readings rather than one

Checking a single reading only proves the sensor worked once. The faults found during this build were mostly intermittent or partial, so the thing worth testing is consistency across a run. A sensor that reads correctly and then corrupts is exactly the failure a single glance at the Serial Monitor would miss.

## Why the bounds come from the datasheet

The DHT11 is specified for 0–50 °C and 20–90 % RH, and `analogRead` on this board returns 0–1023. Using those figures rather than arbitrary ones means a value outside the range is not merely unusual for the room, it is outside what the hardware can legitimately report — so it indicates a fault or corruption rather than an unusual environment. The same bounds become detection rules later (see [ROADMAP.md](../ROADMAP.md) Phase 8).
