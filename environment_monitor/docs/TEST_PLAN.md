# Test Plan: OT Environment Monitor

## Purpose

This document defines the test cases used to verify each hardware module and the combined system, following a bring-up-in-isolation-then-integrate approach (see PLANNING.md). Each module was tested individually via the Serial Monitor before being combined into the main sketch, so that integration faults could be isolated from component faults.

## Test Methodology

For each module: power and continuity are verified with a multimeter before applying power; the module is then tested in isolation using a dedicated test sketch (`src/tests/`); expected output is compared against actual output; any failure is diagnosed using a structured elimination process (power → ground → signal continuity → alternate pin → library/software) before concluding a component fault.

## Test Cases

### TC-01: Board and toolchain bring-up

| Field | Detail |
|---|---|
| Objective | Confirm the Arduino Mega2560, USB connection, and IDE toolchain function correctly |
| Procedure | Upload the built-in Blink example; observe onboard LED |
| Expected Result | Onboard LED (pin 13) blinks at a steady 1-second interval |
| Actual Result | LED blinked as expected |
| Status | **Pass** |

### TC-02: Photoresistor (ambient light level)

| Field | Detail |
|---|---|
| Objective | Confirm the photoresistor voltage divider produces a varying analog reading proportional to light level |
| Procedure | Upload `photoresistor_test.ino`; open Serial Monitor; cover sensor with hand, then expose to light |
| Expected Result | Reading (0–1023) decreases when covered, increases in light |
| Actual Result | Reading responded correctly in both directions |
| Status | **Pass** |

### TC-03: LCD1602 display

| Field | Detail |
|---|---|
| Objective | Confirm the LCD initialises and displays text correctly |
| Procedure | Upload `lcd_test.ino`; check backlight, contrast, and displayed characters |
| Expected Result | Backlight on, contrast adjustable, static test message visible |
| Actual Result | Initial failure: backlight off (power fault), then backlight on but no characters (R/W pin found to be floating despite appearing wired — confirmed via fluctuating, non-steady continuity reading rather than a clean beep). Resolved by re-seating the R/W-to-GND connection. Passed after fix. |
| Status | **Pass (after fix — see PLANNING.md Update Log)** |

### TC-04: DS1307 real-time clock

| Field | Detail |
|---|---|
| Objective | Confirm the RTC keeps accurate time and retains it on power loss |
| Procedure | Upload `rtc_test.ino`; force-set to compile time; verify against actual time; power-cycle and re-check |
| Expected Result | Displayed time matches actual time and continues correctly after power loss |
| Actual Result | Initial run showed incorrect time (module was already "running" with a stale time, so the conditional `isrunning()` check skipped setting it); resolved by force-setting the clock once, then reverting to the conditional set. Correct thereafter. |
| Status | **Pass (after fix)** |

### TC-05: DHT11 temperature/humidity sensor

| Field | Detail |
|---|---|
| Objective | Confirm the DHT11 returns valid temperature and humidity readings |
| Procedure | Upload `dht11_test.ino`; check Serial Monitor for valid readings vs. error codes |
| Expected Result | Temperature and humidity values printed, updating every ~2 seconds |
| Actual Result | Consistent `SimpleDHTErrStartLow` error (sensor produced no response signal at all) across multiple attempts. Diagnosed via elimination: confirmed 5V present at sensor (multimeter, corrected for an initial AC/resistance-mode measurement error), confirmed GND and DATA line continuity end-to-end, tried an alternate digital pin, confirmed correct library installed, added external 10kOhm pull-up. All checks passed with no change in fault. |
| Status | **Fail — hardware fault, not wiring.** Root-caused to a faulty sensor unit. Replacement ordered; retest pending. |

### TC-06: Combined system (light + RTC + LCD)

| Field | Detail |
|---|---|
| Objective | Confirm all working modules run simultaneously without pin or timing conflicts |
| Procedure | Upload `ot_environment_monitor.ino`; observe LCD for concurrent, correctly updating time and light readings |
| Expected Result | Top row shows ticking time (HH:MM:SS); bottom row shows live light level; no interference between modules |
| Actual Result | Both rows update correctly and independently; no pin conflicts (LCD on D7–D12, RTC on I2C D20/D21, photoresistor on A0) |
| Status | **Pass** |

### TC-07: DHT11 retest with replacement unit

| Field | Detail |
|---|---|
| Objective | Confirm the replacement DHT11 returns valid temperature and humidity readings in isolation |
| Procedure | Upload `dht11_test.ino` to the replacement unit; check Serial Monitor for valid readings vs. error codes |
| Expected Result | Temperature and humidity values printed, updating every ~2 seconds, no error codes |
| Actual Result | Clean readings, no errors — confirms the original unit (TC-05) was a genuine hardware fault, not a wiring or code issue |
| Status | **Pass** |

### TC-08: Full combined system (light + RTC + LCD + DHT11)

| Field | Detail |
|---|---|
| Objective | Confirm the replacement DHT11 integrates into the combined sketch without disrupting existing functionality |
| Procedure | Upload the updated `ot_environment_monitor.ino` (with DHT11 added); observe LCD for all four readings updating concurrently |
| Expected Result | Time, temperature, humidity, and light level all display and update correctly; no pin or timing conflicts |
| Actual Result | All four readings displayed correctly and updated concurrently with no pin or timing conflicts (DHT11 throttled to a 2s read interval independent of the 1s time/light refresh) |
| Status | **Pass** |

## Summary

| Test Case | Module | Status |
|---|---|---|
| TC-01 | Board/toolchain | Pass |
| TC-02 | Photoresistor | Pass |
| TC-03 | LCD1602 | Pass (after fix) |
| TC-04 | DS1307 RTC | Pass (after fix) |
| TC-05 | DHT11 (original unit) | Fail (hardware fault) |
| TC-06 | Combined system (light + RTC + LCD) | Pass |
| TC-07 | DHT11 (replacement unit, isolated) | Pass |
| TC-08 | Full combined system (all 4 modules) | Pass |

All test cases above pass. The build is functionally complete. Additional test cases below cover the control theory extension.

### TC-09: Relay module bring-up (bang-bang control extension)

| Field | Detail |
|---|---|
| Objective | Confirm the relay module switches a motor circuit on/off in response to DHT11 temperature readings with hysteresis |
| Procedure | Upload `relay_test.ino`; warm the DHT11 past the on-threshold and confirm relay click, motor spin, and Serial output; verify power reaches the load side (multimeter voltage check at NO while energized); verify continuity across COM/NO while energized |
| Expected Result | Relay clicks on/off at the correct thresholds; motor spins while relay is energized; continuity confirmed across COM/NO while energized |
| Actual Result | Relay coil/control side confirmed working (audible click at correct thresholds, correct Serial output). Motor confirmed working when powered directly, bypassing the relay. However, no continuity measured across COM/NO even while the relay was actively energized — isolating the fault to the relay's mechanical switching contacts specifically, not the control side, wiring, motor, or power supply. |
| Status | **Fail — hardware fault, not wiring.** Relay module's load-side contacts are faulty. Diagnosed via the same elimination methodology used for TC-05 (DHT11): control signal confirmed, power confirmed, motor confirmed, wiring continuity confirmed everywhere except across the relay's own switching contacts. |

## Summary (Control Extension)

| Test Case | Module | Status |
|---|---|---|
| TC-09 | Relay module | Fail (hardware fault) |
