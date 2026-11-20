
import pandas as pd
import pytest

from geopulse.stop_data_generator import (
    generate_stop_scenario_data,
    STOP_DURATIONS_MINUTES,
)


def test_default_device_count():
    data = generate_stop_scenario_data()

    assert data["DeviceID"].nunique() == 20


def test_custom_device_count():
    data = generate_stop_scenario_data(num_devices=5)

    assert data["DeviceID"].nunique() == 5


def test_expected_record_count():
    data = generate_stop_scenario_data(num_devices=2)

    # 24 stationary points + 3 movement points per device.
    assert len(data) == 54


def test_required_columns():
    data = generate_stop_scenario_data()

    assert list(data.columns) == [
        "DeviceID",
        "Lat",
        "Long",
        "Timestamp",
    ]


def test_reproducible_seed():
    first = generate_stop_scenario_data(seed=42)
    second = generate_stop_scenario_data(seed=42)

    pd.testing.assert_frame_equal(first, second)


def test_different_seeds():
    first = generate_stop_scenario_data(seed=42)
    second = generate_stop_scenario_data(seed=99)

    assert not first.equals(second)


def test_records_are_sorted():
    data = generate_stop_scenario_data()

    for _, group in data.groupby("DeviceID"):
        assert group["Timestamp"].is_monotonic_increasing


def test_valid_coordinates():
    data = generate_stop_scenario_data()

    assert data["Lat"].between(-90, 90).all()
    assert data["Long"].between(-180, 180).all()


def test_expected_stop_durations_are_configured():
    assert STOP_DURATIONS_MINUTES == (10, 15, 30, 45)


def test_invalid_device_count():
    with pytest.raises(ValueError, match="num_devices"):
        generate_stop_scenario_data(num_devices=0)


def test_invalid_seed():
    with pytest.raises(ValueError, match="seed"):
        generate_stop_scenario_data(seed=1.5)


def test_invalid_start_time():
    with pytest.raises(ValueError, match="start_time"):
        generate_stop_scenario_data(start_time="invalid-date")
