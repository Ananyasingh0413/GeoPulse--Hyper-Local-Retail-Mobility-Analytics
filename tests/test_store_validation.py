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

def test_missing_store_coordinates():
    stores = pd.DataFrame({
        "StoreID": ["S001", "S002"],
        "StoreName": ["Store A", "Store B"],
        "Lat": [None, 28.67],
        "Long": [77.15, None]
    })

    results = validate_store_data(stores)

    assert results["missing_latitudes"] == 1
    assert results["missing_longitudes"] == 1


def test_missing_store_ids():
    stores = pd.DataFrame({
        "StoreID": [None, "S002"],
        "StoreName": ["Store A", "Store B"],
        "Lat": [28.65, 28.67],
        "Long": [77.15, 77.18]
    })

    results = validate_store_data(stores)

    assert results["missing_store_ids"] == 1


def test_missing_store_names():
    stores = pd.DataFrame({
        "StoreID": ["S001", "S002"],
        "StoreName": [None, "Store B"],
        "Lat": [28.65, 28.67],
        "Long": [77.15, 77.18]
    })

    results = validate_store_data(stores)

    assert results["missing_store_names"] == 1


def test_empty_store_names():
    stores = pd.DataFrame({
        "StoreID": ["S001", "S002"],
        "StoreName": ["", "   "],
        "Lat": [28.65, 28.67],
        "Long": [77.15, 77.18]
    })

    results = validate_store_data(stores)

    assert results["empty_store_names"] == 2


def test_duplicate_store_coordinates():
    stores = pd.DataFrame({
        "StoreID": ["S001", "S002", "S003"],
        "StoreName": ["Store A", "Store B", "Store C"],
        "Lat": [28.65, 28.65, 28.67],
        "Long": [77.15, 77.15, 77.18]
    })

    results = validate_store_data(stores)

    assert results["duplicate_coordinates"] == 1


def test_zero_store_coordinates():
    stores = pd.DataFrame({
        "StoreID": ["S001"],
        "StoreName": ["Store A"],
        "Lat": [0],
        "Long": [0]
    })

    results = validate_store_data(stores)

    assert results["zero_coordinate_rows"] == 1