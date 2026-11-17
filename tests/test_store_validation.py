import pandas as pd

from geopulse.store_validation import validate_store_data


def test_valid_store_data():
    stores = pd.DataFrame({
        "StoreID": ["S001", "S002"],
        "StoreName": ["Store A", "Store B"],
        "Lat": [28.65, 28.67],
        "Long": [77.15, 77.18]
    })

    results = validate_store_data(stores)

    assert results["missing_columns"] == []
    assert results["duplicate_store_ids"] == 0
    assert results["empty_store_ids"] == 0
    assert results["empty_store_names"] == 0
    assert results["invalid_latitudes"] == 0
    assert results["invalid_longitudes"] == 0


def test_duplicate_store_ids():
    stores = pd.DataFrame({
        "StoreID": ["S001", "S001"],
        "StoreName": ["Store A", "Store B"],
        "Lat": [28.65, 28.67],
        "Long": [77.15, 77.18]
    })

    results = validate_store_data(stores)

    assert results["duplicate_store_ids"] == 1


def test_invalid_coordinates():
    stores = pd.DataFrame({
        "StoreID": ["S001", "S002"],
        "StoreName": ["Store A", "Store B"],
        "Lat": [95, 28.67],
        "Long": [77.15, 200]
    })

    results = validate_store_data(stores)

    assert results["invalid_latitudes"] == 1
    assert results["invalid_longitudes"] == 1