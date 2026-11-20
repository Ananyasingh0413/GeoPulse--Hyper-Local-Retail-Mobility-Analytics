
import numpy as np
import pandas as pd

from geopulse.trajectory import haversine_distance_km


REQUIRED_COLUMNS = ["DeviceID", "Lat", "Long", "Timestamp"]

DEFAULT_STOP_RADIUS_METERS = 100
DEFAULT_MIN_DWELL_MINUTES = 10
DEFAULT_MAX_GAP_MINUTES = 10


def detect_gps_stops(
    data,
    stop_radius_meters=DEFAULT_STOP_RADIUS_METERS,
    min_dwell_minutes=DEFAULT_MIN_DWELL_MINUTES,
    max_gap_minutes=DEFAULT_MAX_GAP_MINUTES,
):
    """
    Detect stationary GPS stops for individual devices.

    A stop is identified when consecutive GPS points remain
    within the configured radius of the first point and
    consecutive observations do not exceed the maximum gap.

    Dwell time is measured between the first and last
    observations of a detected stop.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    missing = set(REQUIRED_COLUMNS) - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError("GPS dataset cannot be empty")

    if (
        not np.isfinite(stop_radius_meters)
        or stop_radius_meters <= 0
    ):
        raise ValueError("Stop radius must be positive")

    if (
        not np.isfinite(min_dwell_minutes)
        or min_dwell_minutes <= 0
    ):
        raise ValueError("Minimum dwell time must be positive")

    if (
        not np.isfinite(max_gap_minutes)
        or max_gap_minutes <= 0
    ):
        raise ValueError("Maximum gap must be positive")

    result = data[REQUIRED_COLUMNS].copy()

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

    max_gap = pd.Timedelta(minutes=max_gap_minutes)

    detected_stops = []

    def save_stop(device_id, points, stop_number):
        if len(points) < 2:
            return

        start_time = points[0]["Timestamp"]
        end_time = points[-1]["Timestamp"]

        dwell_minutes = (
            end_time - start_time
        ).total_seconds() / 60

        if dwell_minutes < min_dwell_minutes:
            return

        latitudes = [point["Lat"] for point in points]
        longitudes = [point["Long"] for point in points]

        detected_stops.append({
            "DeviceID": device_id,
            "StopID": f"{device_id}_S{stop_number:03d}",
            "StartTime": start_time,
            "EndTime": end_time,
            "DwellMinutes": dwell_minutes,
            "PointCount": len(points),
            "Lat": float(np.mean(latitudes)),
            "Long": float(np.mean(longitudes)),
        })

    for device_id, group in result.groupby(
        "DeviceID", sort=False
    ):
        records = group.to_dict("records")

        current_stop = []
        anchor_lat = None
        anchor_long = None
        stop_number = 0

        for point in records:
            if not current_stop:
                current_stop = [point]
                anchor_lat = point["Lat"]
                anchor_long = point["Long"]
                continue

            previous_time = current_stop[-1]["Timestamp"]

            time_gap = point["Timestamp"] - previous_time

            distance_meters = (
                haversine_distance_km(
                    anchor_lat,
                    anchor_long,
                    point["Lat"],
                    point["Long"],
                ) * 1000
            )

            if (
                time_gap <= pd.Timedelta(0)
                or time_gap > max_gap
                or distance_meters > stop_radius_meters
            ):
                stop_number += 1

                save_stop(
                    device_id,
                    current_stop,
                    stop_number,
                )

                current_stop = [point]
                anchor_lat = point["Lat"]
                anchor_long = point["Long"]

            else:
                current_stop.append(point)

        if current_stop:
            stop_number += 1

            save_stop(
                device_id,
                current_stop,
                stop_number,
            )

    output_columns = [
        "DeviceID",
        "StopID",
        "StartTime",
        "EndTime",
        "DwellMinutes",
        "PointCount",
        "Lat",
        "Long",
    ]

    return pd.DataFrame(
        detected_stops,
        columns=output_columns,
    )
