
from pathlib import Path

import pandas as pd

from .config import (
    GPS_DATA_PATH,
    STORE_DATA_PATH,
    CATCHMENT_DATA_PATH,
    GPS_REQUIRED_COLUMNS,
    STORE_REQUIRED_COLUMNS,
)


def _load_csv(path, required_columns=None):
    """Load a CSV file with consistent validation and error handling."""

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Dataset path is not a file: {file_path}"
        )

    if file_path.stat().st_size == 0:
        raise ValueError(
            f"Dataset file is empty: {file_path}"
        )

    try:
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            f"Dataset contains no readable columns: {file_path}"
        ) from exc
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"Invalid CSV structure in: {file_path}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Unsupported text encoding in: {file_path}"
        ) from exc

    if data.empty:
        raise ValueError(
            f"Dataset contains no records: {file_path}"
        )

    if required_columns:
        missing_columns = [
            column for column in required_columns
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns in {file_path}: "
                f"{missing_columns}"
            )

    return data


def load_gps_data(path=GPS_DATA_PATH):
    """Load and validate the GPS dataset."""
    return _load_csv(path, GPS_REQUIRED_COLUMNS)


def load_store_data(path=STORE_DATA_PATH):
    """Load and validate the store dataset."""
    return _load_csv(path, STORE_REQUIRED_COLUMNS)


def load_catchment_data(path=CATCHMENT_DATA_PATH):
    """Load the catchment analysis dataset."""
    return _load_csv(path)


def load_custom_csv(path, required_columns=None):
    """Load a custom CSV dataset with optional column validation."""
    return _load_csv(path, required_columns)
