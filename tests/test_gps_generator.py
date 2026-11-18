
import pandas as pd
import pytest

from geopulse.gps_generator import (
    generate_gps_data,
    save_gps_data,
)


def test_default_record_count():
    gps = generate_gps_data()

    assert len(gps) == 1000


def test_custom_record_count():
    gps = generate_gps_data(num_records=500)

    assert len(gps) == 500


def test_required_columns():
    gps = generate_gps_data()

    assert list(gps.columns) == [
        "DeviceID",
        "Lat",
        "Long",
        "Timestamp",
    ]


def test_device_count():
    gps = generate_gps_data(
        num_records=500,
        num_devices=25,
    )

    assert gps["DeviceID"].nunique() <= 25
    assert gps["DeviceID"].nunique() > 0


def test_reproducible_seed():
    first = generate_gps_data(seed=123)
    second = generate_gps_data(seed=123)

    pd.testing.assert_frame_equal(first, second)


def test_different_seeds():
    first = generate_gps_data(seed=123)
    second = generate_gps_data(seed=456)

    assert not first.equals(second)


def test_valid_coordinates():
    gps = generate_gps_data()

    assert gps["Lat"].between(-90, 90).all()
    assert gps["Long"].between(-180, 180).all()


def test_custom_coordinate_bounds():
    gps = generate_gps_data(
        num_records=200,
        lat_bounds=(28.5, 28.7),
        long_bounds=(77.0, 77.2),
    )

    assert gps["Lat"].between(28.5, 28.7).all()
    assert gps["Long"].between(77.0, 77.2).all()


def test_valid_timestamps():
    gps = generate_gps_data()

    assert pd.api.types.is_datetime64_any_dtype(
        gps["Timestamp"]
    )
    assert gps["Timestamp"].notna().all()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"num_records": 0},
        {"num_records": -10},
        {"num_devices": 0},
        {"num_devices": -5},
        {"start_time": "2026-11-05", "end_time": "2026-11-01"},
        {"lat_bounds": (-100, 90)},
        {"long_bounds": (-180, 200)},
    ],
)
def test_invalid_generator_inputs(kwargs):
    with pytest.raises(ValueError):
        generate_gps_data(**kwargs)


def test_save_csv(tmp_path):
    gps = generate_gps_data(num_records=50)
    output = tmp_path / "gps_test.csv"

    saved_path = save_gps_data(gps, output)

    assert saved_path.exists()

    loaded = pd.read_csv(saved_path)

    assert len(loaded) == 50


def test_prevent_overwrite(tmp_path):
    gps = generate_gps_data(num_records=10)
    output = tmp_path / "gps_test.csv"

    save_gps_data(gps, output)

    with pytest.raises(FileExistsError):
        save_gps_data(gps, output)


def test_allow_overwrite(tmp_path):
    gps = generate_gps_data(num_records=10)
    output = tmp_path / "gps_test.csv"

    save_gps_data(gps, output)
    saved_path = save_gps_data(
        gps,
        output,
        overwrite=True,
    )

    assert saved_path.exists()


def test_missing_columns_rejected(tmp_path):
    invalid_data = pd.DataFrame({
        "DeviceID": ["D001"],
        "Lat": [28.6],
    })

    with pytest.raises(ValueError):
        save_gps_data(
            invalid_data,
            tmp_path / "invalid.csv",
        )
