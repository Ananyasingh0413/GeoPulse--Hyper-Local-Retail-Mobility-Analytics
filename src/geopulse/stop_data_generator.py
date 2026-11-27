
import numpy as np
import pandas as pd


STOP_DURATIONS_MINUTES = (10, 15, 30, 45)
SAMPLING_INTERVAL_MINUTES = 5


def generate_stop_scenario_data(
    num_devices=20,
    start_time="2026-11-20 08:00:00",
    seed=42,
):
    """Generate reproducible GPS data with known stationary stops."""

    if (
        not isinstance(num_devices, int)
        or isinstance(num_devices, bool)
        or num_devices <= 0
    ):
        raise ValueError("num_devices must be a positive integer")

    if seed is not None and (
        not isinstance(seed, int) or isinstance(seed, bool)
    ):
        raise ValueError("seed must be an integer or None")

    try:
        start = pd.Timestamp(start_time)
    except (TypeError, ValueError):
        raise ValueError("Invalid start_time") from None

    if pd.isna(start):
        raise ValueError("Invalid start_time")

    rng = np.random.default_rng(seed)
    records = []

    for device_number in range(1, num_devices + 1):
        device_id = f"D{device_number:03d}"

        base_lat = rng.uniform(28.55, 28.75)
        base_long = rng.uniform(77.05, 77.25)

        device_start = start + pd.Timedelta(
            minutes=(device_number - 1) * 5
        )

        for stop_index, duration in enumerate(
            STOP_DURATIONS_MINUTES
        ):
            center_lat = base_lat + stop_index * 0.006
            center_long = base_long + stop_index * 0.006

            point_count = (
                duration // SAMPLING_INTERVAL_MINUTES
            ) + 1

            stop_start = device_start

            for point_index in range(point_count):
                timestamp = stop_start + pd.Timedelta(
                    minutes=point_index * SAMPLING_INTERVAL_MINUTES
                )

                # Small coordinate variation simulates GPS noise.
                lat = center_lat + rng.normal(0, 0.000015)
                long = center_long + rng.normal(0, 0.000015)

                records.append({
                    "DeviceID": device_id,
                    "Lat": lat,
                    "Long": long,
                    "Timestamp": timestamp,
                })

            last_stop_time = stop_start + pd.Timedelta(
                minutes=duration
            )

            device_start = last_stop_time + pd.Timedelta(minutes=5)

            # Add a midpoint observation between stop locations.
            if stop_index < len(STOP_DURATIONS_MINUTES) - 1:
                next_lat = base_lat + (stop_index + 1) * 0.006
                next_long = base_long + (stop_index + 1) * 0.006

                records.append({
                    "DeviceID": device_id,
                    "Lat": (center_lat + next_lat) / 2,
                    "Long": (center_long + next_long) / 2,
                    "Timestamp": device_start,
                })

                device_start += pd.Timedelta(minutes=5)

    result = pd.DataFrame(records)

    return result.sort_values(
        ["DeviceID", "Timestamp"]
    ).reset_index(drop=True)
