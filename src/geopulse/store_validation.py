
import pandas as pd

from .config import STORE_REQUIRED_COLUMNS


def validate_store_data(stores):
    results = {}

    # Check required columns
    missing_columns = [
        column for column in STORE_REQUIRED_COLUMNS
        if column not in stores.columns
    ]

    results["missing_columns"] = missing_columns

    # Check missing values
    results["missing_values"] = (
        stores.isnull().sum().to_dict()
    )

    # Check duplicate rows
    results["duplicate_rows"] = int(
        stores.duplicated().sum()
    )

    # Check duplicate Store IDs
    if "StoreID" in stores.columns:
        results["duplicate_store_ids"] = int(
            stores["StoreID"].duplicated().sum()
        )

        results["empty_store_ids"] = int(
            stores["StoreID"]
            .astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
            .sum()
        )

    # Check empty store names
    if "StoreName" in stores.columns:
        results["empty_store_names"] = int(
            stores["StoreName"]
            .astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
            .sum()
        )

    # Validate latitude
    if "Lat" in stores.columns:
        latitude = pd.to_numeric(
            stores["Lat"], errors="coerce"
        )

        results["non_numeric_latitudes"] = int(
            (stores["Lat"].notna() & latitude.isna()).sum()
        )

        results["invalid_latitudes"] = int(
            (
                latitude.notna()
                & ~latitude.between(-90, 90)
            ).sum()
        )

    # Validate longitude
    if "Long" in stores.columns:
        longitude = pd.to_numeric(
            stores["Long"], errors="coerce"
        )

        results["non_numeric_longitudes"] = int(
            (stores["Long"].notna() & longitude.isna()).sum()
        )

        results["invalid_longitudes"] = int(
            (
                longitude.notna()
                & ~longitude.between(-180, 180)
            ).sum()
        )

    return results
