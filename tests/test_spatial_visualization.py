
import pandas as pd
import pytest

from geopulse.visualization import generate_spatial_map


@pytest.fixture
def gps_data():
    return pd.DataFrame({
        "DeviceID": ["D001", "D002"],
        "Lat": [28.6500, 28.7000],
        "Long": [77.1500, 77.2000],
        "Timestamp": [
            "2026-11-20 08:00:00",
            "2026-11-20 08:05:00"
        ]
    })


@pytest.fixture
def store_data():
    return pd.DataFrame({
        "StoreID": ["S001", "S002"],
        "StoreName": ["Store A", "Store B"],
        "Lat": [28.6500, 28.6700],
        "Long": [77.1500, 77.1800]
    })


def test_generates_interactive_map(
    gps_data, store_data, tmp_path
):
    output_path = tmp_path / "spatial_map.html"

    result = generate_spatial_map(
        gps_data,
        store_data,
        output_path
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_map_contains_store_information(
    gps_data, store_data, tmp_path
):
    output_path = tmp_path / "store_map.html"

    generate_spatial_map(
        gps_data,
        store_data,
        output_path
    )

    html = output_path.read_text(encoding="utf-8")

    assert "Store A" in html
    assert "Store B" in html
    assert "S001" in html
    assert "S002" in html


def test_map_contains_visualization_layers(
    gps_data, store_data, tmp_path
):
    output_path = tmp_path / "layers_map.html"

    generate_spatial_map(
        gps_data,
        store_data,
        output_path
    )

    html = output_path.read_text(encoding="utf-8")

    assert "Stores and 500m Catchments" in html
    assert "All GPS Observations" in html
    assert "Matched Catchment Observations" in html


def test_map_supports_custom_catchment_radius(
    gps_data, store_data, tmp_path
):
    output_path = tmp_path / "custom_radius.html"

    generate_spatial_map(
        gps_data,
        store_data,
        output_path,
        radius_meters=1000
    )

    html = output_path.read_text(encoding="utf-8")

    assert "1000" in html
    assert "Stores and 1000m Catchments" in html


def test_rejects_invalid_gps_input(
    store_data, tmp_path
):
    output_path = tmp_path / "invalid_gps.html"

    with pytest.raises(TypeError):
        generate_spatial_map(
            [],
            store_data,
            output_path
        )


def test_rejects_invalid_store_input(
    gps_data, tmp_path
):
    output_path = tmp_path / "invalid_store.html"

    with pytest.raises(TypeError):
        generate_spatial_map(
            gps_data,
            [],
            output_path
        )


def test_rejects_missing_gps_columns(
    store_data, tmp_path
):
    gps = pd.DataFrame({
        "DeviceID": ["D001"],
        "Lat": [28.6500]
    })

    with pytest.raises(ValueError):
        generate_spatial_map(
            gps,
            store_data,
            tmp_path / "missing_gps.html"
        )


def test_rejects_missing_store_columns(
    gps_data, tmp_path
):
    stores = pd.DataFrame({
        "StoreID": ["S001"],
        "Lat": [28.6500]
    })

    with pytest.raises(ValueError):
        generate_spatial_map(
            gps_data,
            stores,
            tmp_path / "missing_store.html"
        )
