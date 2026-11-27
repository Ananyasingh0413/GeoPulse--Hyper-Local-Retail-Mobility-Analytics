
import pandas as pd
import pytest

from geopulse.temporal import (
    analyze_hourly_footfall,
    analyze_daily_footfall,
    compare_weekday_weekend_footfall,
    analyze_store_peak_hours,
)


@pytest.fixture
def sessions():
    return pd.DataFrame({
        "StoreID": ["S001", "S001", "S003", "S003"],
        "StoreName": ["Store A", "Store A", "Store C", "Store C"],
        "DeviceID": ["D001", "D001", "D002", "D003"],
        "EntryTime": [
            "2026-11-20 12:20:00",
            "2026-11-20 12:45:00",
            "2026-11-21 14:25:00",
            "2026-11-21 14:40:00",
        ],
    })


def test_hourly_footfall(sessions):
    result = analyze_hourly_footfall(sessions)

    assert len(result) == 24
    assert result.loc[result["Hour"] == 12, "TotalVisits"].iloc[0] == 2
    assert result.loc[result["Hour"] == 14, "TotalVisits"].iloc[0] == 2
    assert result["TotalVisits"].sum() == 4


def test_hourly_unique_visitors(sessions):
    result = analyze_hourly_footfall(sessions)

    hour_12 = result[result["Hour"] == 12].iloc[0]

    assert hour_12["UniqueVisitors"] == 1


def test_daily_footfall(sessions):
    result = analyze_daily_footfall(sessions)

    assert len(result) == 2
    assert result["TotalVisits"].tolist() == [2, 2]


def test_weekday_weekend_comparison(sessions):
    result = compare_weekday_weekend_footfall(sessions)

    weekday = result[result["DayType"] == "Weekday"].iloc[0]
    weekend = result[result["DayType"] == "Weekend"].iloc[0]

    assert weekday["TotalVisits"] == 2
    assert weekend["TotalVisits"] == 2


def test_store_peak_hours(sessions):
    result = analyze_store_peak_hours(sessions)

    store_a = result[result["StoreID"] == "S001"].iloc[0]
    store_c = result[result["StoreID"] == "S003"].iloc[0]

    assert store_a["PeakHour"] == 12
    assert store_c["PeakHour"] == 14


def test_multiple_peak_hours():
    data = pd.DataFrame({
        "StoreID": ["S001", "S001", "S001"],
        "StoreName": ["Store A"] * 3,
        "DeviceID": ["D001", "D002", "D003"],
        "EntryTime": [
            "2026-11-20 10:00:00",
            "2026-11-20 12:00:00",
            "2026-11-20 12:30:00",
        ],
    })

    result = analyze_store_peak_hours(data)

    assert result["PeakHour"].tolist() == [12]
    assert result["TotalVisits"].tolist() == [2]


def test_empty_sessions():
    empty = pd.DataFrame(columns=[
        "StoreID", "StoreName", "DeviceID", "EntryTime"
    ])

    assert len(analyze_hourly_footfall(empty)) == 24
    assert analyze_hourly_footfall(empty)["TotalVisits"].sum() == 0
    assert analyze_daily_footfall(empty).empty
    assert compare_weekday_weekend_footfall(empty)["TotalVisits"].sum() == 0
    assert analyze_store_peak_hours(empty).empty


def test_missing_required_column():
    invalid = pd.DataFrame({
        "StoreID": ["S001"],
        "StoreName": ["Store A"],
        "DeviceID": ["D001"],
    })

    with pytest.raises(ValueError, match="Missing required session columns"):
        analyze_hourly_footfall(invalid)


def test_invalid_timestamp():
    invalid = pd.DataFrame({
        "StoreID": ["S001"],
        "StoreName": ["Store A"],
        "DeviceID": ["D001"],
        "EntryTime": ["invalid-date"],
    })

    with pytest.raises(ValueError, match="invalid timestamps"):
        analyze_daily_footfall(invalid)


def test_null_session_values():
    invalid = pd.DataFrame({
        "StoreID": ["S001"],
        "StoreName": ["Store A"],
        "DeviceID": [None],
        "EntryTime": ["2026-11-20 12:00:00"],
    })

    with pytest.raises(ValueError, match="cannot contain null"):
        analyze_hourly_footfall(invalid)


def test_non_dataframe_input():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        analyze_daily_footfall([])
