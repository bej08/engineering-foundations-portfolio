"""
conftest.py

Shared pytest fixtures.

The serial fixture is the important one: it skips rather than fails when no
Arduino is attached. A hardware test that fails on a machine without the
hardware is not a useful signal, so absence of a device is reported as
"skipped" and a genuine device fault is reported as "failed".
"""

import os

import pytest

BAUD_RATE = int(os.environ.get("MONITOR_BAUD", "9600"))


def find_serial_port():
    """Return the configured port, or auto-detect a likely Arduino."""
    configured = os.environ.get("MONITOR_SERIAL_PORT")
    if configured:
        return configured

    try:
        from serial.tools import list_ports
    except ImportError:
        return None

    for port in list_ports.comports():
        name = port.device.lower()
        if "usbmodem" in name or "usbserial" in name or "ttyacm" in name:
            return port.device
    return None


@pytest.fixture(scope="session")
def serial_connection():
    """
    Open the Arduino's serial port for the whole test session.

    Skips the tests that need it if pyserial is missing, no device is found,
    or the port cannot be opened (usually because the Arduino IDE's Serial
    Monitor is holding it).
    """
    try:
        import serial
    except ImportError:
        pytest.skip("pyserial not installed")

    port = find_serial_port()
    if port is None:
        pytest.skip("no Arduino serial port found")

    try:
        connection = serial.Serial(port, BAUD_RATE, timeout=5)
    except serial.SerialException as exc:
        pytest.skip(f"could not open {port}: {exc}")

    # The board resets when the port opens, so wait for it to come back and
    # discard the partial line that reset produces.
    import time

    time.sleep(2)
    connection.reset_input_buffer()

    yield connection

    connection.close()
