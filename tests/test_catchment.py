import pandas as pd

from geopulse.catchment import (
    calculate_store_distances,
    summarize_catchment,
    analyze_catchments
)


def test_distance_calculation():
    gps = pd.DataFrame({
        "DeviceID": ["D001"],
        "Lat": [28.6500],
        "Long": [77.1500]
    })

    stores = pd.DataFrame({
        "StoreID": ["S001"],
        "StoreName": ["Store A"],
        "Lat": [28.6500],
        "Long": [77.1500]
    })

    distances = calculate_store_distances(gps, stores)

    assert len(distances) == 1
    assert distances.iloc[0]["Distance_Meters"] == 0
    assert distances.iloc[0]["Within_Catchment"] == True


def test_catchment_summary():
    distances = pd.DataFrame({
        "DeviceID": ["D001", "D002", "D003"],
        "StoreID": ["S001", "S001", "S001"],
        "StoreName": ["Store A", "Store A", "Store A"],
        "Distance_Meters": [100, 300, 700],
        "Within_Catchment": [True, True, False]
    })

    summary = summarize_catchment(distances)

    assert summary.iloc[0]["Devices_Within_500m"] == 2


def test_complete_catchment_analysis():
    gps = pd.DataFrame({
        "DeviceID": ["D001"],
        "Lat": [28.6500],
        "Long": [77.1500]
    })

    stores = pd.DataFrame({
        "StoreID": ["S001"],
        "StoreName": ["Store A"],
        "Lat": [28.6500],
        "Long": [77.1500]
    })

    distances, summary = analyze_catchments(gps, stores)

    assert len(distances) == 1
    assert len(summary) == 1
    assert summary.iloc[0]["Devices_Within_500m"] == 1