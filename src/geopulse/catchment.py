
import pandas as pd
from geopy.distance import geodesic

from .config import CATCHMENT_RADIUS_METERS


def calculate_store_distances(gps, stores):
    """
    Calculate the distance between every GPS record and each store.
    """

    distance_records = []

    for gps_row in gps.itertuples(index=False):
        gps_location = (gps_row.Lat, gps_row.Long)

        for store_row in stores.itertuples(index=False):
            store_location = (store_row.Lat, store_row.Long)

            distance_meters = geodesic(
                gps_location,
                store_location
            ).meters

            distance_records.append({
                "DeviceID": gps_row.DeviceID,
                "StoreID": store_row.StoreID,
                "StoreName": store_row.StoreName,
                "Distance_Meters": round(distance_meters, 2),
                "Within_Catchment": (
                    distance_meters <= CATCHMENT_RADIUS_METERS
                )
            })

    return pd.DataFrame(distance_records)


def summarize_catchment(distances):
    """
    Generate store-wise unique device counts within the catchment radius.
    """

    summary_records = []

    for store_id in distances["StoreID"].unique():
        store_data = distances[
            distances["StoreID"] == store_id
        ]

        within_radius = store_data[
            store_data["Within_Catchment"]
        ]

        summary_records.append({
            "StoreID": store_id,
            "StoreName": store_data["StoreName"].iloc[0],
            "Devices_Within_500m": (
                within_radius["DeviceID"].nunique()
            )
        })

    return pd.DataFrame(summary_records)


def analyze_catchments(gps, stores):
    """
    Run complete store-wise catchment analysis.
    """

    distances = calculate_store_distances(gps, stores)

    summary = summarize_catchment(distances)

    return distances, summary
