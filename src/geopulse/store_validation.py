
import pandas as pd

from .config import STORE_REQUIRED_COLUMNS


def validate_store_data(stores):
    """Validate store records and return data quality metrics."""

    results = {
        "missing_columns": [
            column for column in STORE_REQUIRED_COLUMNS
            if column not in stores.columns
        ],
        "missing_values": stores.isnull().sum().to_dict(),
        "duplicate_rows": int(stores.duplicated().sum()),
    }

    metrics = {
        "duplicate_store_ids": 0,
        "empty_store_ids": 0,
        "empty_store_names": 0,
        "missing_store_ids": 0,
        "missing_store_names": 0,
        "non_numeric_latitudes": 0,
        "non_numeric_longitudes": 0,
        "invalid_latitudes": 0,
        "invalid_longitudes": 0,
        "missing_latitudes": 0,
        "missing_longitudes": 0,
        "duplicate_coordinates": 0,
        "zero_coordinate_rows": 0,
    }

    latitude = None
    longitude = None

    if "StoreID" in stores.columns:
        store_ids = stores["StoreID"].astype("string").str.strip()

        metrics["missing_store_ids"] = int(
            stores["StoreID"].isna().sum()
        )

        metrics["empty_store_ids"] = int(
            store_ids.eq("").fillna(False).sum()
        )

        valid_ids = store_ids.notna() & store_ids.ne("")

        metrics["duplicate_store_ids"] = int(
            store_ids[valid_ids].duplicated().sum()
        )

    if "StoreName" in stores.columns:
        store_names = stores["StoreName"].astype("string").str.strip()

        metrics["missing_store_names"] = int(
            stores["StoreName"].isna().sum()
        )

        metrics["empty_store_names"] = int(
            store_names.eq("").fillna(False).sum()
        )

    if "Lat" in stores.columns:
        latitude = pd.to_numeric(stores["Lat"], errors="coerce")

        metrics["missing_latitudes"] = int(stores["Lat"].isna().sum())

        metrics["non_numeric_latitudes"] = int(
            (stores["Lat"].notna() & latitude.isna()).sum()
        )

        metrics["invalid_latitudes"] = int(
            (latitude.notna() & ~latitude.between(-90, 90)).sum()
        )

    if "Long" in stores.columns:
        longitude = pd.to_numeric(stores["Long"], errors="coerce")

        metrics["missing_longitudes"] = int(stores["Long"].isna().sum())

        metrics["non_numeric_longitudes"] = int(
            (stores["Long"].notna() & longitude.isna()).sum()
        )

        metrics["invalid_longitudes"] = int(
            (longitude.notna() & ~longitude.between(-180, 180)).sum()
        )

    if latitude is not None and longitude is not None:
        valid_coordinates = (
            latitude.between(-90, 90)
            & longitude.between(-180, 180)
        )

        coordinates = pd.DataFrame({
            "Lat": latitude[valid_coordinates],
            "Long": longitude[valid_coordinates],
        })

        metrics["duplicate_coordinates"] = int(
            coordinates.duplicated().sum()
        )

        metrics["zero_coordinate_rows"] = int(
            (latitude.eq(0) & longitude.eq(0)).sum()
        )

    results.update(metrics)

    return results
