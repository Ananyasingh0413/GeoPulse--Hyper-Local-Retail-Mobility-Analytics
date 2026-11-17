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