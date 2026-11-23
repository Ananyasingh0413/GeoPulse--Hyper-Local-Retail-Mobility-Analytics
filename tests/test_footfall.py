
import pandas as pd
import pytest

from geopulse.footfall import (
    detect_visit_sessions,
    calculate_footfall_metrics,
)


def make_gps_data(points):
    return pd.DataFrame(
        points,
        columns=["DeviceID", "Lat", "Long", "Timestamp"],
    )


def make_store_data():
    return pd.DataFrame([
        ("S001", "Store A", 28.6139, 77.2090),
    ], columns=[
        "StoreID",
        "StoreName",
        "Lat",
        "Long",
    ])


def test_detects_single_ongoing_visit():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6140, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6141, 77.2090, "2026-11-20 08:10:00"),
    ])

    sessions = detect_visit_sessions(gps, make_store_data())

    assert len(sessions) == 1
    assert sessions.iloc[0]["DeviceID"] == "D001"
    assert sessions.iloc[0]["Observations"] == 3
    assert sessions.iloc[0]["Status"] == "ongoing"


def test_completes_visit_after_two_outside_points():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:10:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:15:00"),
    ])

    sessions = detect_visit_sessions(gps, make_store_data())

    assert len(sessions) == 1
    assert sessions.iloc[0]["Status"] == "completed"
    assert sessions.iloc[0]["ExitTime"] == pd.Timestamp(
        "2026-11-20 08:10:00"
    )
    assert sessions.iloc[0]["Observations"] == 2


def test_ignores_temporary_outside_observation():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:10:00"),
    ])

    sessions = detect_visit_sessions(gps, make_store_data())

    assert len(sessions) == 1
    assert sessions.iloc[0]["Status"] == "ongoing"
    assert sessions.iloc[0]["Observations"] == 3


def test_detects_separate_repeat_visits():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:10:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:15:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:20:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:25:00"),
    ])

    sessions = detect_visit_sessions(gps, make_store_data())

    assert len(sessions) == 2
    assert sessions["DeviceID"].nunique() == 1
    assert sessions["Status"].tolist() == [
        "completed",
        "ongoing",
    ]


def test_closes_session_when_gps_gap_exceeds_limit():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:30:00"),
    ])

    sessions = detect_visit_sessions(gps, make_store_data())

    assert len(sessions) == 2
    assert sessions.iloc[0]["Status"] == "incomplete"
    assert sessions.iloc[1]["Status"] == "ongoing"


def test_sorts_unsorted_gps_records():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:10:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:05:00"),
    ])

    sessions = detect_visit_sessions(gps, make_store_data())

    assert len(sessions) == 1
    assert sessions.iloc[0]["EntryTime"] == pd.Timestamp(
        "2026-11-20 08:00:00"
    )


def test_rejects_empty_gps_data():
    gps = make_gps_data([])

    with pytest.raises(ValueError, match="cannot be empty"):
        detect_visit_sessions(gps, make_store_data())


def test_rejects_duplicate_device_timestamps():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
    ])

    with pytest.raises(ValueError, match="Duplicate GPS timestamps"):
        detect_visit_sessions(gps, make_store_data())


def test_rejects_missing_device_id():
    gps = make_gps_data([
        (None, 28.6139, 77.2090, "2026-11-20 08:00:00"),
    ])

    with pytest.raises(ValueError, match="DeviceID"):
        detect_visit_sessions(gps, make_store_data())


def test_rejects_invalid_exit_confirmation():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
    ])

    with pytest.raises(ValueError, match="positive integer"):
        detect_visit_sessions(
            gps,
            make_store_data(),
            exit_confirmation_points=0,
        )


def test_calculates_store_footfall_metrics():
    sessions = pd.DataFrame([
        ("S001", "Store A", "D001"),
        ("S001", "Store A", "D001"),
        ("S001", "Store A", "D002"),
        ("S002", "Store B", "D003"),
    ], columns=["StoreID", "StoreName", "DeviceID"])

    metrics = calculate_footfall_metrics(sessions)

    store_a = metrics[metrics["StoreID"] == "S001"].iloc[0]

    assert store_a["UniqueVisitors"] == 2
    assert store_a["TotalVisits"] == 3
    assert store_a["RepeatVisitors"] == 1
    assert store_a["AverageVisitsPerVisitor"] == 1.5
    assert store_a["FootfallRank"] == 1


def test_returns_empty_metrics_for_empty_sessions():
    sessions = pd.DataFrame(
        columns=["StoreID", "StoreName", "DeviceID"]
    )

    metrics = calculate_footfall_metrics(sessions)

    assert metrics.empty
    assert "TotalVisits" in metrics.columns


def test_ranks_stores_by_total_visits():
    sessions = pd.DataFrame([
        ("S001", "Store A", "D001"),
        ("S001", "Store A", "D002"),
        ("S002", "Store B", "D003"),
    ], columns=["StoreID", "StoreName", "DeviceID"])

    metrics = calculate_footfall_metrics(sessions)

    store_a = metrics[metrics["StoreID"] == "S001"].iloc[0]
    store_b = metrics[metrics["StoreID"] == "S002"].iloc[0]

    assert store_a["FootfallRank"] == 1
    assert store_b["FootfallRank"] == 2



def test_uses_consecutive_observations_for_gap_detection():
    gps = make_gps_data([
        ("D001", 28.6139, 77.2090, "2026-11-20 08:00:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:05:00"),
        ("D001", 28.6200, 77.2090, "2026-11-20 08:15:00"),
    ])

    sessions = detect_visit_sessions(
        gps,
        make_store_data(),
        max_gap_minutes=10,
        exit_confirmation_points=2,
    )

    assert len(sessions) == 1
    assert sessions.iloc[0]["Status"] == "completed"
    assert sessions.iloc[0]["ExitTime"] == pd.Timestamp(
        "2026-11-20 08:05:00"
    )