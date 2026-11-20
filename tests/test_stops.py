
import pandas as pd
import pytest

from geopulse.stops import detect_gps_stops


def make_gps_data(points):
    return pd.DataFrame(
        points,
        columns=["DeviceID", "Lat", "Long", "Timestamp"],
    )


def test_detects_valid_stationary_stop():
    data = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6141, 77.2090, "2026-11-20 08:10:00"),
        ("D001", 28.6140, 77.2091, "2026-11-20 08:15:00"),
    ])

    stops = detect_gps_stops(data)

    assert len(stops) == 1
    assert stops.iloc[0]["DeviceID"] == "D001"
    assert stops.iloc[0]["DwellMinutes"] == 15
    assert stops.iloc[0]["PointCount"] == 4


def test_ignores_stop_below_minimum_dwell():
    data = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:05:00"),
    ])

    stops = detect_gps_stops(data)

    assert stops.empty


def test_separates_different_devices():
    data = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6141, 77.2090, "2026-11-20 08:10:00"),
        ("D002", 28.6200, 77.2200, "2026-11-20 08:00:00"),
        ("D002", 28.6201, 77.2200, "2026-11-20 08:05:00"),
        ("D002", 28.6202, 77.2200, "2026-11-20 08:10:00"),
    ])

    stops = detect_gps_stops(data)

    assert len(stops) == 2
    assert set(stops["DeviceID"]) == {"D001", "D002"}


def test_splits_stop_when_time_gap_exceeds_limit():
    data = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6141, 77.2090, "2026-11-20 08:30:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:35:00"),
    ])

    stops = detect_gps_stops(data)

    assert stops.empty


def test_splits_stop_when_distance_exceeds_radius():
    data = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:10:00"),
        ("D001", 28.6201, 77.2090, "2026-11-20 08:15:00"),
    ])

    stops = detect_gps_stops(data)

    assert stops.empty


def test_sorts_unsorted_gps_records():
    data = make_gps_data([
        ("D001", 28.6141, 77.2090, "2026-11-20 08:10:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:05:00"),
    ])

    stops = detect_gps_stops(data)

    assert len(stops) == 1
    assert stops.iloc[0]["DwellMinutes"] == 10


def test_rejects_missing_required_column():
    data = pd.DataFrame({
        "DeviceID": ["D001"],
        "Lat": [28.6139],
        "Timestamp": ["2026-11-20 08:00:00"],
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        detect_gps_stops(data)


def test_rejects_invalid_latitude():
    data = make_gps_data([
        ("D001", 95.0, 77.2090, "2026-11-20 08:00:00"),
    ])

    with pytest.raises(ValueError, match="Latitude"):
        detect_gps_stops(data)


def test_rejects_empty_dataframe():
    data = make_gps_data([])

    with pytest.raises(ValueError, match="cannot be empty"):
        detect_gps_stops(data)


def test_rejects_invalid_stop_radius():
    data = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
    ])

    with pytest.raises(ValueError, match="Stop radius"):
        detect_gps_stops(data, stop_radius_meters=0)


def test_rejects_missing_device_id():
    data = make_gps_data([
        (None, 28.6139, 77.2090, "2026-11-20 08:00:00"),
    ])

    with pytest.raises(ValueError, match="DeviceID"):
        detect_gps_stops(data)
