
import pandas as pd
import pytest

from pyproj import Transformer

from geopulse.spatial import analyze_spatial_catchments


def create_gps(latitudes, longitudes, device_ids=None):
    count = len(latitudes)

    if device_ids is None:
        device_ids = [f"D{i:03d}" for i in range(count)]

    return pd.DataFrame({
        "DeviceID": device_ids,
        "Lat": latitudes,
        "Long": longitudes,
        "Timestamp": ["2026-11-20 08:00:00"] * count
    })


def create_stores(latitudes=None, longitudes=None):
    if latitudes is None:
        latitudes = [28.6500]

    if longitudes is None:
        longitudes = [77.1500]

    return pd.DataFrame({
        "StoreID": [f"S{i:03d}" for i in range(len(latitudes))],
        "StoreName": [f"Store {i}" for i in range(len(latitudes))],
        "Lat": latitudes,
        "Long": longitudes
    })


def test_gps_point_at_store_location():
    gps = create_gps([28.6500], [77.1500])
    stores = create_stores()

    matches, unmatched, summary = analyze_spatial_catchments(
        gps, stores
    )

    assert len(matches) == 1
    assert len(unmatched) == 0
    assert matches.iloc[0]["Distance_Meters"] == 0
    assert summary.iloc[0]["Unique_Devices"] == 1


def test_gps_point_inside_500m_catchment():
    transformer = Transformer.from_crs(
        "EPSG:4326", "EPSG:32643", always_xy=True
    )
    reverse = Transformer.from_crs(
        "EPSG:32643", "EPSG:4326", always_xy=True
    )

    x, y = transformer.transform(77.1500, 28.6500)
    longitude, latitude = reverse.transform(x + 499, y)

    gps = create_gps([latitude], [longitude])
    stores = create_stores()

    matches, unmatched, _ = analyze_spatial_catchments(
        gps, stores
    )

    assert len(matches) == 1
    assert len(unmatched) == 0
    assert matches.iloc[0]["Distance_Meters"] < 500


def test_gps_point_outside_500m_catchment():
    transformer = Transformer.from_crs(
        "EPSG:4326", "EPSG:32643", always_xy=True
    )
    reverse = Transformer.from_crs(
        "EPSG:32643", "EPSG:4326", always_xy=True
    )

    x, y = transformer.transform(77.1500, 28.6500)
    longitude, latitude = reverse.transform(x + 501, y)

    gps = create_gps([latitude], [longitude])
    stores = create_stores()

    matches, unmatched, _ = analyze_spatial_catchments(
        gps, stores
    )

    assert len(matches) == 0
    assert len(unmatched) == 1


def test_500m_boundary_is_included():
    transformer = Transformer.from_crs(
        "EPSG:4326", "EPSG:32643", always_xy=True
    )
    reverse = Transformer.from_crs(
        "EPSG:32643", "EPSG:4326", always_xy=True
    )

    x, y = transformer.transform(77.1500, 28.6500)
    longitude, latitude = reverse.transform(x + 500, y)

    gps = create_gps([latitude], [longitude])
    stores = create_stores()

    matches, _, _ = analyze_spatial_catchments(
        gps, stores
    )

    assert len(matches) == 1
    assert matches.iloc[0]["Distance_Meters"] <= 500


def test_overlapping_store_catchments():
    gps = create_gps([28.6500], [77.1500])

    stores = create_stores(
        latitudes=[28.6500, 28.6500],
        longitudes=[77.1500, 77.1510]
    )

    matches, unmatched, summary = analyze_spatial_catchments(
        gps, stores
    )

    assert len(matches) == 2
    assert len(unmatched) == 0
    assert summary["Total_GPS_Visits"].sum() == 2


def test_zero_match_stores_are_preserved():
    gps = create_gps([28.6500], [77.1500])

    stores = create_stores(
        latitudes=[28.6500, 28.7000],
        longitudes=[77.1500, 77.2000]
    )

    _, _, summary = analyze_spatial_catchments(gps, stores)

    assert len(summary) == 2
    assert summary.iloc[0]["Total_GPS_Visits"] == 1
    assert summary.iloc[1]["Total_GPS_Visits"] == 0


def test_invalid_coordinates_are_rejected():
    gps = create_gps([95.0], [77.1500])
    stores = create_stores()

    with pytest.raises(ValueError):
        analyze_spatial_catchments(gps, stores)


def test_geographic_crs_is_rejected():
    gps = create_gps([28.6500], [77.1500])
    stores = create_stores()

    with pytest.raises(ValueError):
        analyze_spatial_catchments(
            gps,
            stores,
            projected_crs="EPSG:4326"
        )
