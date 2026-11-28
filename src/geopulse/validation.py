
import pandas as pd

from .config import GPS_REQUIRED_COLUMNS


def validate_gps_data(gps):
    """Validate GPS records and return a structured quality summary."""

    results = {
        "missing_columns": [
            column for column in GPS_REQUIRED_COLUMNS
            if column not in gps.columns
        ],
        "missing_values": gps.isnull().sum().to_dict(),
        "duplicate_rows": int(gps.duplicated().sum()),
    }

    # Initialize metrics so incomplete datasets remain safe to validate.
    metrics = {
        "missing_latitudes": 0,
        "missing_longitudes": 0,
        "missing_timestamps": 0,
        "missing_device_ids": 0,
        "empty_device_ids": 0,
        "non_numeric_latitudes": 0,
        "non_numeric_longitudes": 0,
        "invalid_latitudes": 0,
        "invalid_longitudes": 0,
        "invalid_timestamps": 0,
        "duplicate_device_timestamps": 0,
        "zero_coordinate_rows": 0,
    }

    latitude = None
    longitude = None
    timestamps = None
    device_ids = None

    # Latitude validation
    if "Lat" in gps.columns:
        latitude = pd.to_numeric(gps["Lat"], errors="coerce")

        metrics["missing_latitudes"] = int(gps["Lat"].isna().sum())

        metrics["non_numeric_latitudes"] = int(
            (gps["Lat"].notna() & latitude.isna()).sum()
        )

        metrics["invalid_latitudes"] = int(
            (latitude.notna() & ~latitude.between(-90, 90)).sum()
        )

    # Longitude validation
    if "Long" in gps.columns:
        longitude = pd.to_numeric(gps["Long"], errors="coerce")

        metrics["missing_longitudes"] = int(gps["Long"].isna().sum())

        metrics["non_numeric_longitudes"] = int(
            (gps["Long"].notna() & longitude.isna()).sum()
        )

        metrics["invalid_longitudes"] = int(
            (longitude.notna() & ~longitude.between(-180, 180)).sum()
        )

    # Timestamp validation
    if "Timestamp" in gps.columns:
        timestamps = pd.to_datetime(
            gps["Timestamp"],
            errors="coerce",
            format="mixed",
            utc=True
        )

        metrics["missing_timestamps"] = int(
            gps["Timestamp"].isna().sum()
        )

        metrics["invalid_timestamps"] = int(
            (gps["Timestamp"].notna() & timestamps.isna()).sum()
        )

    # Device ID validation
    if "DeviceID" in gps.columns:
        device_ids = gps["DeviceID"].astype("string").str.strip()

        metrics["missing_device_ids"] = int(
            gps["DeviceID"].isna().sum()
        )

        metrics["empty_device_ids"] = int(
            device_ids.eq("").fillna(False).sum()
        )

    # Detect suspicious zero-coordinate records.
    if latitude is not None and longitude is not None:
        metrics["zero_coordinate_rows"] = int(
            (latitude.eq(0) & longitude.eq(0)).sum()
        )

    # Detect repeated timestamps for the same valid device.
    if device_ids is not None and timestamps is not None:
        valid_records = (
            device_ids.notna()
            & device_ids.ne("")
            & timestamps.notna()
        )

        duplicate_mask = pd.DataFrame({
            "DeviceID": device_ids[valid_records],
            "Timestamp": timestamps[valid_records],
        }).duplicated()

        metrics["duplicate_device_timestamps"] = int(
            duplicate_mask.sum()
        )

    results.update(metrics)

    return results
