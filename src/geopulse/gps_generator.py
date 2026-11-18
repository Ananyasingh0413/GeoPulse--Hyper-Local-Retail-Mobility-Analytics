
from pathlib import Path

import numpy as np
import pandas as pd


def generate_gps_data(
    num_records=1000,
    num_devices=100,
    start_time="2026-11-01",
    end_time="2026-11-05",
    seed=42,
    lat_bounds=(28.40, 28.90),
    long_bounds=(76.80, 77.40),
):
    """Generate reproducible synthetic GPS mobility records."""

    if not isinstance(num_records, int) or isinstance(num_records, bool):
        raise ValueError("num_records must be an integer.")

    if not isinstance(num_devices, int) or isinstance(num_devices, bool):
        raise ValueError("num_devices must be an integer.")

    if num_records <= 0:
        raise ValueError("num_records must be greater than zero.")

    if num_devices <= 0:
        raise ValueError("num_devices must be greater than zero.")

    if seed is not None and (
        not isinstance(seed, int) or isinstance(seed, bool)
    ):
        raise ValueError("seed must be an integer or None.")

    if len(lat_bounds) != 2 or len(long_bounds) != 2:
        raise ValueError("Coordinate bounds must contain two values.")

    lat_min, lat_max = map(float, lat_bounds)
    long_min, long_max = map(float, long_bounds)

    if not (-90 <= lat_min < lat_max <= 90):
        raise ValueError("Invalid latitude bounds.")

    if not (-180 <= long_min < long_max <= 180):
        raise ValueError("Invalid longitude bounds.")

    try:
        start = pd.Timestamp(start_time)
        end = pd.Timestamp(end_time)
    except (TypeError, ValueError):
        raise ValueError("Invalid timestamp range.") from None

    if pd.isna(start) or pd.isna(end):
        raise ValueError("Invalid timestamp range.")

    if start.tz != end.tz:
        raise ValueError("Start and end timestamps must use the same timezone.")

    if start >= end:
        raise ValueError("start_time must be earlier than end_time.")

    rng = np.random.default_rng(seed)

    start_ns = start.value
    end_ns = end.value

    random_timestamps = rng.integers(
        start_ns,
        end_ns,
        size=num_records,
        dtype=np.int64,
    )

    device_numbers = rng.integers(
        1,
        num_devices + 1,
        size=num_records,
    )

    gps_data = pd.DataFrame({
        "DeviceID": [
            f"D{number:03d}" for number in device_numbers
        ],
        "Lat": rng.uniform(lat_min, lat_max, num_records),
        "Long": rng.uniform(long_min, long_max, num_records),
        "Timestamp": pd.to_datetime(random_timestamps),
    })

    return gps_data


def save_gps_data(gps_data, output_path, overwrite=False):
    """Save generated GPS records to CSV safely."""

    required_columns = ["DeviceID", "Lat", "Long", "Timestamp"]

    if not isinstance(gps_data, pd.DataFrame):
        raise TypeError("gps_data must be a pandas DataFrame.")

    missing_columns = [
        column for column in required_columns
        if column not in gps_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"File already exists: {output_path}. "
            "Use overwrite=True to replace it."
        )

    gps_data.to_csv(output_path, index=False)

    return output_path
