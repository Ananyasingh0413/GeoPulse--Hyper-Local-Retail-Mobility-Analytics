
import numpy as np
import pandas as pd

from geopulse.config import CATCHMENT_RADIUS_METERS
from geopulse.catchment import calculate_store_distances


REQUIRED_GPS_COLUMNS = [
    "DeviceID",
    "Lat",
    "Long",
    "Timestamp",
]

REQUIRED_STORE_COLUMNS = [
    "StoreID",
    "StoreName",
    "Lat",
    "Long",
]

DEFAULT_MAX_GAP_MINUTES = 10
DEFAULT_EXIT_CONFIRMATION_POINTS = 2


def detect_visit_sessions(
    gps_data,
    stores,
    catchment_radius_meters=CATCHMENT_RADIUS_METERS,
    max_gap_minutes=DEFAULT_MAX_GAP_MINUTES,
    exit_confirmation_points=DEFAULT_EXIT_CONFIRMATION_POINTS,
):
    """
    Detect store visit sessions from GPS observations.

    A session starts when a device enters a store catchment.
    It closes after the configured number of consecutive
    outside observations.

    Long GPS gaps produce incomplete sessions.
    Sessions still active at dataset end are marked ongoing.
    """

    if not isinstance(gps_data, pd.DataFrame):
        raise TypeError("GPS data must be a pandas DataFrame")

    if not isinstance(stores, pd.DataFrame):
        raise TypeError("Stores must be a pandas DataFrame")

    missing_gps = (
        set(REQUIRED_GPS_COLUMNS) - set(gps_data.columns)
    )

    missing_stores = (
        set(REQUIRED_STORE_COLUMNS) - set(stores.columns)
    )

    if missing_gps:
        raise ValueError(
            f"Missing GPS columns: {sorted(missing_gps)}"
        )

    if missing_stores:
        raise ValueError(
            f"Missing store columns: {sorted(missing_stores)}"
        )

    if gps_data.empty:
        raise ValueError("GPS dataset cannot be empty")

    if stores.empty:
        raise ValueError("Store dataset cannot be empty")

    if (
        not np.isfinite(catchment_radius_meters)
        or catchment_radius_meters <= 0
    ):
        raise ValueError("Catchment radius must be positive")

    if (
        not np.isfinite(max_gap_minutes)
        or max_gap_minutes <= 0
    ):
        raise ValueError("Maximum GPS gap must be positive")

    if (
        not isinstance(exit_confirmation_points, int)
        or isinstance(exit_confirmation_points, bool)
        or exit_confirmation_points < 1
    ):
        raise ValueError(
            "Exit confirmation points must be a positive integer"
        )

    gps = gps_data[REQUIRED_GPS_COLUMNS].copy()
    store_data = stores[REQUIRED_STORE_COLUMNS].copy()

    if gps["DeviceID"].isna().any():
        raise ValueError("DeviceID cannot contain missing values")

    if store_data[["StoreID", "StoreName"]].isna().any().any():
        raise ValueError("Store identifiers cannot be missing")

    if gps["Timestamp"].isna().any():
        raise ValueError("Timestamp cannot contain missing values")

    gps["Timestamp"] = pd.to_datetime(
        gps["Timestamp"], errors="raise"
    )

    if gps["Timestamp"].isna().any():
        raise ValueError("Timestamp cannot contain missing values")

    if gps.duplicated(["DeviceID", "Timestamp"]).any():
        raise ValueError(
            "Duplicate GPS timestamps found for a device"
        )

    for column in ["Lat", "Long"]:
        gps[column] = pd.to_numeric(
            gps[column], errors="raise"
        )

        store_data[column] = pd.to_numeric(
            store_data[column], errors="raise"
        )

        if not np.isfinite(gps[column]).all():
            raise ValueError(f"GPS {column} must be finite")

        if not np.isfinite(store_data[column]).all():
            raise ValueError(f"Store {column} must be finite")

    if not gps["Lat"].between(-90, 90).all():
        raise ValueError("GPS latitude is out of range")

    if not gps["Long"].between(-180, 180).all():
        raise ValueError("GPS longitude is out of range")

    if not store_data["Lat"].between(-90, 90).all():
        raise ValueError("Store latitude is out of range")

    if not store_data["Long"].between(-180, 180).all():
        raise ValueError("Store longitude is out of range")

    if store_data["StoreID"].duplicated().any():
        raise ValueError("StoreID values must be unique")

    gps = gps.sort_values(
        ["DeviceID", "Timestamp"]
    ).reset_index(drop=True)

    stores_count = len(store_data)

    gps["GPS_Row"] = np.arange(len(gps))

    distances = calculate_store_distances(
        gps,
        store_data,
    )

    distances["GPS_Row"] = (
        distances.index // stores_count
    )

    distances = distances.merge(
        gps[["GPS_Row", "Timestamp"]],
        on="GPS_Row",
        validate="many_to_one",
    )

    distances["Within_Catchment"] = (
        distances["Distance_Meters"]
        <= catchment_radius_meters
    )

    max_gap = pd.Timedelta(
        minutes=max_gap_minutes
    )

    sessions = []

    def save_session(
        store_id,
        store_name,
        device_id,
        points,
        status,
        exit_time=pd.NaT,
    ):
        first_point = points[0]
        last_point = points[-1]

        sessions.append({
            "StoreID": store_id,
            "StoreName": store_name,
            "DeviceID": device_id,
            "EntryTime": first_point["Timestamp"],
            "LastSeenTime": last_point["Timestamp"],
            "ExitTime": exit_time,
            "Observations": len(points),
            "Status": status,
        })

    for (store_id, device_id), group in distances.groupby(
        ["StoreID", "DeviceID"],
        sort=False,
    ):
        group = group.sort_values(
            "Timestamp"
        ).reset_index(drop=True)

        store_name = group.iloc[0]["StoreName"]

        current_session = []
        pending_exit = []
        previous_observation_time = None

        for point in group.to_dict("records"):

            if previous_observation_time is not None:
                time_gap = (
                    point["Timestamp"] - previous_observation_time
                )

                if time_gap <= pd.Timedelta(0):
                    raise ValueError(
                        "GPS timestamps must increase per device"
                    )

                if time_gap > max_gap:
                    if current_session:
                        save_session(
                            store_id,
                            store_name,
                            device_id,
                            current_session,
                            "incomplete",
                        )

                    current_session = []
                    pending_exit = []

            previous_observation_time = point["Timestamp"]

            if point["Within_Catchment"]:

                if current_session:
                    current_session.extend(pending_exit)
                    pending_exit = []

                else:
                    current_session = []

                current_session.append(point)

            elif current_session:

                pending_exit.append(point)

                if len(pending_exit) >= exit_confirmation_points:
                    exit_time = pending_exit[0]["Timestamp"]

                    save_session(
                        store_id,
                        store_name,
                        device_id,
                        current_session,
                        "completed",
                        exit_time,
                    )

                    current_session = []
                    pending_exit = []

        if current_session:
            save_session(
                store_id,
                store_name,
                device_id,
                current_session,
                "ongoing",
            )

    columns = [
        "StoreID",
        "StoreName",
        "DeviceID",
        "EntryTime",
        "LastSeenTime",
        "ExitTime",
        "Observations",
        "Status",
    ]

    return pd.DataFrame(
        sessions,
        columns=columns,
    )


def calculate_footfall_metrics(sessions):
    """
    Calculate store-wise footfall and visit frequency metrics.
    """

    required = [
        "StoreID",
        "StoreName",
        "DeviceID",
    ]

    if not isinstance(sessions, pd.DataFrame):
        raise TypeError("Sessions must be a pandas DataFrame")

    missing = set(required) - set(sessions.columns)

    if missing:
        raise ValueError(
            f"Missing session columns: {sorted(missing)}"
        )

    if sessions.empty:
        return pd.DataFrame(columns=[
            "StoreID",
            "StoreName",
            "UniqueVisitors",
            "TotalVisits",
            "RepeatVisitors",
            "AverageVisitsPerVisitor",
            "FootfallRank",
        ])

    if sessions[required].isna().any().any():
        raise ValueError("Session identifiers cannot be missing")

    metrics = (
        sessions.groupby(
            ["StoreID", "StoreName"],
        )
        .agg(
            UniqueVisitors=("DeviceID", "nunique"),
            TotalVisits=("DeviceID", "size"),
            RepeatVisitors=(
                "DeviceID",
                lambda values: (
                    values.value_counts() > 1
                ).sum(),
            ),
        )
        .reset_index()
    )

    metrics["AverageVisitsPerVisitor"] = (
        metrics["TotalVisits"]
        / metrics["UniqueVisitors"]
    ).round(2)

    metrics["FootfallRank"] = (
        metrics["TotalVisits"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    return metrics.sort_values(
        ["FootfallRank", "StoreID"]
    ).reset_index(drop=True)
