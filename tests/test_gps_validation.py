import pandas as pd

from geopulse.validation import validate_gps_data


def test_valid_gps_data():
    gps = pd.DataFrame({
        "DeviceID": ["D001", "D002"],
        "Lat": [28.65, 28.67],
        "Long": [77.15, 77.18],
        "Timestamp": ["2026-11-01 10:00:00",
                      "2026-11-01 11:00:00"]
    })

    results = validate_gps_data(gps)

    assert results["missing_columns"] == []
    assert results["duplicate_rows"] == 0
    assert results["invalid_latitudes"] == 0
    assert results["invalid_longitudes"] == 0
    assert results["invalid_timestamps"] == 0


def test_invalid_gps_coordinates():
    gps = pd.DataFrame({
        "DeviceID": ["D001", "D002"],
        "Lat": [95, 28.67],
        "Long": [77.15, 200],
        "Timestamp": ["2026-11-01 10:00:00",
                      "2026-11-01 11:00:00"]
    })

    results = validate_gps_data(gps)

    assert results["invalid_latitudes"] == 1
    assert results["invalid_longitudes"] == 1


def test_invalid_gps_timestamp():
    gps = pd.DataFrame({
        "DeviceID": ["D001", "D002"],
        "Lat": [28.65, 28.67],
        "Long": [77.15, 77.18],
        "Timestamp": ["invalid-date", "2026-11-01 11:00:00"]
    })

    results = validate_gps_data(gps)

    assert results["invalid_timestamps"] == 1


def test_missing_gps_coordinates():
    gps = pd.DataFrame({
        "DeviceID": ["D001", "D002"],
        "Lat": [None, 28.67],
        "Long": [77.15, None],
        "Timestamp": ["2026-11-01 10:00:00", "2026-11-01 11:00:00"]
    })

    results = validate_gps_data(gps)

    assert results["missing_latitudes"] == 1
    assert results["missing_longitudes"] == 1


def test_missing_timestamp():
    gps = pd.DataFrame({
        "DeviceID": ["D001"],
        "Lat": [28.65],
        "Long": [77.15],
        "Timestamp": [None]
    })

    results = validate_gps_data(gps)

    assert results["missing_timestamps"] == 1


def test_empty_device_ids():
    gps = pd.DataFrame({
        "DeviceID": ["", "   ", "D001"],
        "Lat": [28.65, 28.66, 28.67],
        "Long": [77.15, 77.16, 77.17],
        "Timestamp": ["2026-11-01 10:00:00"] * 3
    })

    results = validate_gps_data(gps)

    assert results["empty_device_ids"] == 2


def test_duplicate_device_timestamps():
    gps = pd.DataFrame({
        "DeviceID": ["D001", "D001", "D002"],
        "Lat": [28.65, 28.66, 28.67],
        "Long": [77.15, 77.16, 77.17],
        "Timestamp": [
            "2026-11-01 10:00:00",
            "2026-11-01 10:00:00",
            "2026-11-01 11:00:00"
        ]
    })

    results = validate_gps_data(gps)

    assert results["duplicate_device_timestamps"] == 1


def test_zero_coordinate_detection():
    gps = pd.DataFrame({
        "DeviceID": ["D001", "D002"],
        "Lat": [0, 28.65],
        "Long": [0, 77.15],
        "Timestamp": ["2026-11-01 10:00:00"] * 2
    })

    results = validate_gps_data(gps)

    assert results["zero_coordinate_rows"] == 1


def test_non_numeric_coordinates():
    gps = pd.DataFrame({
        "DeviceID": ["D001", "D002"],
        "Lat": ["invalid", 28.65],
        "Long": [77.15, "invalid"],
        "Timestamp": ["2026-11-01 10:00:00"] * 2
    })

    results = validate_gps_data(gps)

    assert results["non_numeric_latitudes"] == 1
    assert results["non_numeric_longitudes"] == 1