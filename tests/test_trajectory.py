
import pandas as pd
import numpy as np
import pytest

from geopulse.trajectory import (
    haversine_distance_km,
    calculate_trajectory_metrics
)


def sample_data():
    return pd.DataFrame({
        "DeviceID": ["D001", "D001", "D001"],
        "Lat": [28.60, 28.61, 28.62],
        "Long": [77.10, 77.11, 77.12],
        "Timestamp": [
            "2026-11-20 08:00:00",
            "2026-11-20 08:05:00",
            "2026-11-20 08:10:00"
        ]
    })


def test_haversine_distance_scalar():
    distance = haversine_distance_km(
        28.60, 77.10, 28.61, 77.11
    )
    assert distance > 0


def test_haversine_distance_array():
    distances = haversine_distance_km(
        np.array([28.60, 28.61]),
        np.array([77.10, 77.11]),
        np.array([28.61, 28.62]),
        np.array([77.11, 77.12])
    )
    assert len(distances) == 2
    assert np.all(distances > 0)


def test_trajectory_output_shape():
    result = calculate_trajectory_metrics(sample_data())
    assert result.shape == (3, 10)


def test_first_record_has_no_previous_point():
    result = calculate_trajectory_metrics(sample_data())
    assert pd.isna(result.iloc[0]["Distance_km"])
    assert pd.isna(result.iloc[0]["Speed_kmh"])


def test_distance_is_positive():
    result = calculate_trajectory_metrics(sample_data())
    assert (result["Distance_km"].dropna() > 0).all()


def test_speed_calculation():
    result = calculate_trajectory_metrics(sample_data())
    assert (result["Speed_kmh"].dropna() > 0).all()


def test_records_are_sorted():
    data = sample_data().iloc[::-1]
    result = calculate_trajectory_metrics(data)

    assert result["Timestamp"].is_monotonic_increasing


def test_missing_columns_rejected():
    data = sample_data().drop(columns=["Lat"])

    with pytest.raises(ValueError):
        calculate_trajectory_metrics(data)


def test_invalid_latitude_rejected():
    data = sample_data()
    data.loc[0, "Lat"] = 95

    with pytest.raises(ValueError):
        calculate_trajectory_metrics(data)


def test_empty_dataframe_rejected():
    data = pd.DataFrame(columns=[
        "DeviceID", "Lat", "Long", "Timestamp"
    ])

    with pytest.raises(ValueError):
        calculate_trajectory_metrics(data)
