
import pandas as pd


REQUIRED_SESSION_COLUMNS = [
    "StoreID",
    "StoreName",
    "DeviceID",
    "EntryTime",
]


def _prepare_sessions(sessions):
    """Validate and prepare detected visit sessions."""

    if not isinstance(sessions, pd.DataFrame):
        raise TypeError("Sessions must be a pandas DataFrame")

    missing = set(REQUIRED_SESSION_COLUMNS) - set(sessions.columns)

    if missing:
        raise ValueError(
            f"Missing required session columns: {sorted(missing)}"
        )

    data = sessions[REQUIRED_SESSION_COLUMNS].copy()

    if data.empty:
        data["EntryTime"] = pd.to_datetime(data["EntryTime"])
        return data

    if data[REQUIRED_SESSION_COLUMNS].isnull().any().any():
        raise ValueError("Session data cannot contain null values")

    try:
        data["EntryTime"] = pd.to_datetime(
            data["EntryTime"],
            errors="raise"
        )
    except (ValueError, TypeError) as exc:
        raise ValueError("EntryTime contains invalid timestamps") from exc

    return data


def analyze_hourly_footfall(sessions):
    """Calculate total visits and unique visitors for each hour."""

    data = _prepare_sessions(sessions)

    result = pd.DataFrame({"Hour": range(24)})

    if data.empty:
        result["TotalVisits"] = 0
        result["UniqueVisitors"] = 0
        return result

    data["Hour"] = data["EntryTime"].dt.hour

    counts = data.groupby("Hour").agg(
        TotalVisits=("DeviceID", "size"),
        UniqueVisitors=("DeviceID", "nunique"),
    )

    result = result.merge(
        counts,
        left_on="Hour",
        right_index=True,
        how="left",
    )

    result[["TotalVisits", "UniqueVisitors"]] = (
        result[["TotalVisits", "UniqueVisitors"]]
        .fillna(0)
        .astype(int)
    )

    return result


def analyze_daily_footfall(sessions):
    """Calculate total visits and unique visitors for each date."""

    data = _prepare_sessions(sessions)

    columns = ["Date", "TotalVisits", "UniqueVisitors"]

    if data.empty:
        return pd.DataFrame(columns=columns)

    data["Date"] = data["EntryTime"].dt.date

    result = (
        data.groupby("Date")
        .agg(
            TotalVisits=("DeviceID", "size"),
            UniqueVisitors=("DeviceID", "nunique"),
        )
        .reset_index()
    )

    return result[columns]


def compare_weekday_weekend_footfall(sessions):
    """Compare weekday and weekend visit patterns."""

    data = _prepare_sessions(sessions)

    categories = ["Weekday", "Weekend"]

    if data.empty:
        return pd.DataFrame({
            "DayType": categories,
            "TotalVisits": [0, 0],
            "UniqueVisitors": [0, 0],
            "DaysObserved": [0, 0],
            "AverageDailyVisits": [0.0, 0.0],
        })

    data["Date"] = data["EntryTime"].dt.date

    data["DayType"] = data["EntryTime"].dt.day_of_week.map(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )

    totals = data.groupby("DayType").agg(
        TotalVisits=("DeviceID", "size"),
        UniqueVisitors=("DeviceID", "nunique"),
    )

    daily = data.groupby(["DayType", "Date"]).size()

    averages = daily.groupby(level=0).mean()
    days = daily.groupby(level=0).size()

    result = pd.DataFrame({"DayType": categories})
    result["TotalVisits"] = result["DayType"].map(
        totals["TotalVisits"]
    ).fillna(0).astype(int)

    result["UniqueVisitors"] = result["DayType"].map(
        totals["UniqueVisitors"]
    ).fillna(0).astype(int)

    result["DaysObserved"] = result["DayType"].map(
        days
    ).fillna(0).astype(int)

    result["AverageDailyVisits"] = result["DayType"].map(
        averages
    ).fillna(0.0)

    return result


def analyze_store_peak_hours(sessions):
    """Identify each store's busiest visiting hour(s)."""

    data = _prepare_sessions(sessions)

    columns = [
        "StoreID",
        "StoreName",
        "PeakHour",
        "TotalVisits",
    ]

    if data.empty:
        return pd.DataFrame(columns=columns)

    data["Hour"] = data["EntryTime"].dt.hour

    counts = (
        data.groupby(["StoreID", "StoreName", "Hour"])
        .size()
        .reset_index(name="TotalVisits")
    )

    peak_counts = counts.groupby(
        ["StoreID", "StoreName"]
    )["TotalVisits"].transform("max")

    result = counts[counts["TotalVisits"] == peak_counts].copy()

    result = result.rename(columns={"Hour": "PeakHour"})

    return result[columns].sort_values(
        ["StoreID", "PeakHour"]
    ).reset_index(drop=True)
