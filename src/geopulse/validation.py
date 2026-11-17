
import pandas as pd

from .config import GPS_REQUIRED_COLUMNS


def validate_gps_data(gps):
    results = {}

    # Check required columns
    missing_columns = [
        column for column in GPS_REQUIRED_COLUMNS
        if column not in gps.columns
    ]

    results["missing_columns"] = missing_columns
    results["missing_values"] = gps.isnull().sum().to_dict()
    results["duplicate_rows"] = int(gps.duplicated().sum())

    # Validate latitude
    if "Lat" in gps.columns:
        latitude = pd.to_numeric(gps["Lat"], errors="coerce")

        results["non_numeric_latitudes"] = int(
            (gps["Lat"].notna() & latitude.isna()).sum()
        )

        results["invalid_latitudes"] = int(
            (latitude.notna() & ~latitude.between(-90, 90)).sum()
        )

    # Validate longitude
    if "Long" in gps.columns:
        longitude = pd.to_numeric(gps["Long"], errors="coerce")

        results["non_numeric_longitudes"] = int(
            (gps["Long"].notna() & longitude.isna()).sum()
        )

        results["invalid_longitudes"] = int(
            (longitude.notna() & ~longitude.between(-180, 180)).sum()
        )

    # Validate timestamps
    if "Timestamp" in gps.columns:
        timestamps = pd.to_datetime(
            gps["Timestamp"],
            errors="coerce",
            format="mixed"
        )

        results["invalid_timestamps"] = int(
            (gps["Timestamp"].notna() & timestamps.isna()).sum()
        )

    # Check empty device IDs
    if "DeviceID" in gps.columns:
        results["empty_device_ids"] = int(
            gps["DeviceID"]
            .astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
            .sum()
        )

    return results
