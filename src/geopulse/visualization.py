
from pathlib import Path

import folium
import pandas as pd
from folium.plugins import FastMarkerCluster

from .spatial import analyze_spatial_catchments
from .config import CATCHMENT_RADIUS_METERS


def generate_spatial_map(
    gps,
    stores,
    output_path,
    radius_meters=CATCHMENT_RADIUS_METERS,
    projected_crs="EPSG:32643"
):
    """
    Generate an interactive Folium map of GeoPulse store catchments
    and GPS observations.

    Returns:
        Path: Location of the generated HTML map.
    """

    if not isinstance(gps, pd.DataFrame):
        raise TypeError("GPS data must be a pandas DataFrame.")

    if not isinstance(stores, pd.DataFrame):
        raise TypeError("Store data must be a pandas DataFrame.")

    required_gps = {"DeviceID", "Lat", "Long", "Timestamp"}
    required_stores = {"StoreID", "StoreName", "Lat", "Long"}

    if not required_gps.issubset(gps.columns):
        raise ValueError("GPS data is missing required columns.")

    if not required_stores.issubset(stores.columns):
        raise ValueError("Store data is missing required columns.")

    matches, unmatched, summary = analyze_spatial_catchments(
        gps,
        stores,
        radius_meters=radius_meters,
        projected_crs=projected_crs
    )

    center = [
        stores["Lat"].astype(float).mean(),
        stores["Long"].astype(float).mean()
    ]

    spatial_map = folium.Map(
        location=center,
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Store locations and catchment boundaries.
    store_layer = folium.FeatureGroup(
        name=f"Stores and {radius_meters}m Catchments",
        show=True
    )

    for _, store in stores.iterrows():
        latitude = float(store["Lat"])
        longitude = float(store["Long"])

        store_id = store["StoreID"]
        store_name = store["StoreName"]

        store_summary = summary[
            summary["StoreID"] == store_id
        ]

        if store_summary.empty:
            unique_devices = 0
            total_visits = 0
        else:
            unique_devices = int(
                store_summary.iloc[0]["Unique_Devices"]
            )
            total_visits = int(
                store_summary.iloc[0]["Total_GPS_Visits"]
            )

        folium.Circle(
            location=[latitude, longitude],
            radius=radius_meters,
            color="#2563eb",
            weight=2,
            fill=True,
            fill_color="#3b82f6",
            fill_opacity=0.12,
            tooltip=f"{store_name} - {radius_meters}m Catchment"
        ).add_to(store_layer)

        folium.Marker(
            location=[latitude, longitude],
            tooltip=f"{store_name} ({store_id})",
            popup=folium.Popup(
                f"""
                <b>{store_name}</b><br>
                Store ID: {store_id}<br>
                Unique Devices: {unique_devices}<br>
                GPS Visits: {total_visits}<br>
                Catchment Radius: {radius_meters}m
                """,
                max_width=250
            ),
            icon=folium.Icon(
                color="blue",
                icon="shopping-cart",
                prefix="fa"
            )
        ).add_to(store_layer)

    store_layer.add_to(spatial_map)

    # All GPS observations using efficient client-side clustering.
    gps_layer = folium.FeatureGroup(
        name="All GPS Observations",
        show=True
    )

    gps_locations = (
        gps[["Lat", "Long"]]
        .astype(float)
        .values
        .tolist()
    )

    FastMarkerCluster(
        data=gps_locations,
        name="GPS Observation Clusters"
    ).add_to(gps_layer)

    gps_layer.add_to(spatial_map)

    # Matched GPS observations with store details.
    matched_layer = folium.FeatureGroup(
        name="Matched Catchment Observations",
        show=True
    )

    if not matches.empty:
        matched_coordinates = matches

        for _, record in matched_coordinates.iterrows():
            latitude = float(record["Lat"])
            longitude = float(record["Long"])

            popup_text = (
                f"<b>Device:</b> {record['DeviceID']}<br>"
                f"<b>Store:</b> {record['StoreName']}<br>"
                f"<b>Distance:</b> "
                f"{record['Distance_Meters']} metres<br>"
                f"<b>Timestamp:</b> {record['Timestamp']}"
            )

            folium.CircleMarker(
                location=[latitude, longitude],
                radius=5,
                color="#dc2626",
                fill=True,
                fill_color="#ef4444",
                fill_opacity=0.85,
                popup=folium.Popup(
                    popup_text,
                    max_width=300
                )
            ).add_to(matched_layer)

    matched_layer.add_to(spatial_map)

    folium.LayerControl(
        collapsed=False
    ).add_to(spatial_map)

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    spatial_map.save(str(output_path))

    return output_path
