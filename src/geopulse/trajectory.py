
import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["DeviceID", "Lat", "Long", "Timestamp"]



def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance between GPS points in kilometers.

    Supports both individual coordinates and NumPy/Pandas arrays.
    """

    earth_radius = 6371.0

    lat1, lon1, lat2, lon2 = np.radians(
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    distance = (
        2 * earth_radius * np.arcsin(np.sqrt(a))
    )

    # Return scalar for scalar input, array for vector input
    return float(distance) if np.ndim(distance) == 0 else distance



def calculate_trajectory_metrics(data):
    """
    Calculate consecutive GPS distance, time difference,
    and movement speed for each device.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    missing = set(REQUIRED_COLUMNS) - set(data.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = data[REQUIRED_COLUMNS].copy()

    if result.empty:
        raise ValueError("GPS dataset cannot be empty")

    if result["DeviceID"].isna().any():
        raise ValueError("DeviceID cannot contain missing values")

    for column in ["Lat", "Long"]:
        result[column] = pd.to_numeric(
            result[column], errors="raise"
        )

        if not np.isfinite(result[column]).all():
            raise ValueError(f"{column} must contain finite values")

    if not result["Lat"].between(-90, 90).all():
        raise ValueError("Latitude must be between -90 and 90")

    if not result["Long"].between(-180, 180).all():
        raise ValueError("Longitude must be between -180 and 180")

    result["Timestamp"] = pd.to_datetime(
        result["Timestamp"], errors="raise"
    )

    if result["Timestamp"].isna().any():
        raise ValueError("Timestamp cannot contain missing values")

    result = result.sort_values(
        ["DeviceID", "Timestamp"]
    ).reset_index(drop=True)

    grouped = result.groupby("DeviceID", sort=False)

    result["Previous_Lat"] = grouped["Lat"].shift(1)
    result["Previous_Long"] = grouped["Long"].shift(1)
    result["Previous_Timestamp"] = grouped["Timestamp"].shift(1)

    result["Distance_km"] = haversine_distance_km(
        result["Previous_Lat"],
        result["Previous_Long"],
        result["Lat"],
        result["Long"]
    )

    result["Time_Difference_hours"] = (
        result["Timestamp"] - result["Previous_Timestamp"]
    ).dt.total_seconds() / 3600

    valid_intervals = result["Time_Difference_hours"] > 0

    result.loc[~valid_intervals, "Distance_km"] = np.nan

    result["Speed_kmh"] = (
        result["Distance_km"]
        / result["Time_Difference_hours"]
    )

    return result
