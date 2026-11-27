
import numpy as np
import pandas as pd
import geopandas as gpd

from pyproj import CRS

from .config import CATCHMENT_RADIUS_METERS


GPS_COLUMNS = ["DeviceID", "Lat", "Long", "Timestamp"]
STORE_COLUMNS = ["StoreID", "StoreName", "Lat", "Long"]

DEFAULT_PROJECTED_CRS = "EPSG:32643"


def _validate_dataset(data, required_columns, dataset_name):
    """Validate input DataFrame structure and geographic coordinates."""

    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"{dataset_name} must be a pandas DataFrame.")

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"{dataset_name} is missing columns: {missing}"
        )

    if data.empty:
        raise ValueError(f"{dataset_name} cannot be empty.")

    result = data.copy()

    if result[required_columns[0]].isna().any():
        raise ValueError(
            f"{required_columns[0]} cannot contain null values."
        )

    if dataset_name == "Stores":
        if result["StoreID"].duplicated().any():
            raise ValueError("StoreID values must be unique.")

        if result["StoreName"].isna().any():
            raise ValueError("StoreName cannot contain null values.")

    result["Lat"] = pd.to_numeric(result["Lat"], errors="coerce")
    result["Long"] = pd.to_numeric(result["Long"], errors="coerce")

    coordinates = result[["Lat", "Long"]].to_numpy(dtype=float)

    if not np.isfinite(coordinates).all():
        raise ValueError(
            f"{dataset_name} contains invalid coordinates."
        )

    if not result["Lat"].between(-90, 90).all():
        raise ValueError("Latitude must be between -90 and 90.")

    if not result["Long"].between(-180, 180).all():
        raise ValueError("Longitude must be between -180 and 180.")

    return result


def _validate_projected_crs(projected_crs):
    """Ensure the selected CRS uses metres."""

    crs = CRS.from_user_input(projected_crs)

    if not crs.is_projected:
        raise ValueError("A projected CRS is required.")

    if not crs.axis_info:
        raise ValueError("The projected CRS has no axis information.")

    if any(
        abs(axis.unit_conversion_factor - 1.0) > 1e-9
        for axis in crs.axis_info[:2]
    ):
        raise ValueError("The projected CRS must use metres.")

    return crs


def analyze_spatial_catchments(
    gps,
    stores,
    radius_meters=CATCHMENT_RADIUS_METERS,
    projected_crs=DEFAULT_PROJECTED_CRS
):
    """
    Perform GeoPandas-based store catchment analysis.

    Returns:
        matches: GPS records matched to store catchments.
        unmatched: GPS records outside all store catchments.
        summary: Store-wise spatial catchment statistics.
    """

    if (
        not isinstance(radius_meters, (int, float))
        or not np.isfinite(radius_meters)
        or radius_meters <= 0
    ):
        raise ValueError("radius_meters must be a positive number.")

    crs = _validate_projected_crs(projected_crs)

    gps_data = _validate_dataset(
        gps, GPS_COLUMNS, "GPS data"
    )

    store_data = _validate_dataset(
        stores, STORE_COLUMNS, "Stores"
    )

    gps_data = gps_data.reset_index(drop=True)
    gps_data["_gps_index"] = np.arange(len(gps_data))

    gps_gdf = gpd.GeoDataFrame(
        gps_data,
        geometry=gpd.points_from_xy(
            gps_data["Long"],
            gps_data["Lat"]
        ),
        crs="EPSG:4326"
    ).to_crs(crs)

    stores_gdf = gpd.GeoDataFrame(
        store_data,
        geometry=gpd.points_from_xy(
            store_data["Long"],
            store_data["Lat"]
        ),
        crs="EPSG:4326"
    ).to_crs(crs)

    # Preserve store centre coordinates before creating buffers.
    stores_gdf["_store_x"] = stores_gdf.geometry.x
    stores_gdf["_store_y"] = stores_gdf.geometry.y

    buffers_gdf = stores_gdf[
        ["StoreID", "StoreName", "_store_x", "_store_y", "geometry"]
    ].copy()

    buffers_gdf["geometry"] = (
        buffers_gdf.geometry.buffer(radius_meters)
    )

    # Spatial join uses GeoPandas spatial indexing.
    joined = gpd.sjoin(
        gps_gdf,
        buffers_gdf,
        how="inner",
        predicate="intersects"
    )

    if joined.empty:
        matches = pd.DataFrame(columns=[
            "DeviceID",
            "Lat",
            "Long",
            "Timestamp",
            "StoreID",
            "StoreName",
            "Distance_Meters",
            "Within_Catchment"
        ])
    else:
        distances = np.hypot(
            joined.geometry.x - joined["_store_x"],
            joined.geometry.y - joined["_store_y"]
        )

        matches = pd.DataFrame({
            "DeviceID": joined["DeviceID"].to_numpy(),
            "Lat": joined["Lat"].to_numpy(),
            "Long": joined["Long"].to_numpy(),
            "Timestamp": joined["Timestamp"].to_numpy(),
            "StoreID": joined["StoreID"].to_numpy(),
            "StoreName": joined["StoreName"].to_numpy(),
            "Distance_Meters": np.round(distances, 2),
            "Within_Catchment": True
        })

    # Identify original GPS records without any store match.
    matched_indices = set(joined["_gps_index"].tolist())

    unmatched = (
        gps_data.loc[
            ~gps_data["_gps_index"].isin(matched_indices),
            GPS_COLUMNS
        ]
        .reset_index(drop=True)
    )

    # Include every store, even when it has zero matching GPS records.
    if matches.empty:
        summary = pd.DataFrame({
            "StoreID": store_data["StoreID"],
            "StoreName": store_data["StoreName"],
            "Unique_Devices": 0,
            "Total_GPS_Visits": 0
        })
    else:
        counts = (
            matches.groupby(["StoreID", "StoreName"])
            .agg(
                Unique_Devices=("DeviceID", "nunique"),
                Total_GPS_Visits=("DeviceID", "size")
            )
            .reset_index()
        )

        summary = (
            store_data[["StoreID", "StoreName"]]
            .merge(
                counts,
                on=["StoreID", "StoreName"],
                how="left"
            )
        )

        summary[
            ["Unique_Devices", "Total_GPS_Visits"]
        ] = (
            summary[
                ["Unique_Devices", "Total_GPS_Visits"]
            ]
            .fillna(0)
            .astype(int)
        )

    return matches, unmatched, summary
