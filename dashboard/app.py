
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Add project source directory to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from geopulse.footfall import (
    detect_visit_sessions,
    calculate_footfall_metrics,
)
from geopulse.temporal import (
    analyze_hourly_footfall,
    analyze_daily_footfall,
    analyze_store_peak_hours,
)

GPS_PATH = PROJECT_ROOT / "data" / "geopulse_gps_trajectories.csv"
STORE_PATH = PROJECT_ROOT / "data" / "geopulse_store_locations.csv"

st.set_page_config(
    page_title="GeoPulse | Retail Analytics",
    page_icon="📍",
    layout="wide",
)

st.title("GeoPulse Retail Mobility Dashboard")
st.caption("Hyper-Local Retail Mobility Analytics")

@st.cache_data
def load_dashboard_data():
    gps = pd.read_csv(GPS_PATH)
    stores = pd.read_csv(STORE_PATH)

    sessions = detect_visit_sessions(gps, stores)

    return gps, stores, sessions


try:
    gps, stores, sessions = load_dashboard_data()

    if sessions.empty:
        st.warning("No store visits detected in the selected dataset.")
        st.stop()

    st.sidebar.header("Dashboard Filters")

    store_options = stores["StoreName"].tolist()

    selected_stores = st.sidebar.multiselect(
        "Select Stores",
        options=store_options,
        default=store_options,
    )

    selected_ids = stores.loc[
        stores["StoreName"].isin(selected_stores),
        "StoreID",
    ]

    filtered = sessions[
        sessions["StoreID"].isin(selected_ids)
    ].copy()

    if filtered.empty:
        st.info("No visits available for the selected stores.")
        st.stop()

    metrics = calculate_footfall_metrics(filtered)
    hourly = analyze_hourly_footfall(filtered)
    daily = analyze_daily_footfall(filtered)
    peaks = analyze_store_peak_hours(filtered)

    total_visits = len(filtered)
    unique_visitors = filtered["DeviceID"].nunique()
    active_stores = filtered["StoreID"].nunique()
    repeat_visitors = (
        filtered.groupby("DeviceID").size().gt(1).sum()
    )

    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Visits", total_visits)
    col2.metric("Unique Visitors", unique_visitors)
    col3.metric("Active Stores", active_stores)
    col4.metric("Repeat Visitors", int(repeat_visitors))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Hourly Footfall")

        fig_hourly = px.line(
            hourly,
            x="Hour",
            y="TotalVisits",
            markers=True,
            title="Visits by Hour",
            labels={
                "Hour": "Hour of Day",
                "TotalVisits": "Total Visits",
            },
        )

        fig_hourly.update_xaxes(dtick=1)
        st.plotly_chart(fig_hourly, use_container_width=True)

    with right:
        st.subheader("Store Performance")

        fig_store = px.bar(
            metrics,
            x="StoreName",
            y="TotalVisits",
            color="TotalVisits",
            text="TotalVisits",
            title="Visits by Store",
            labels={
                "StoreName": "Store",
                "TotalVisits": "Total Visits",
            },
        )

        st.plotly_chart(fig_store, use_container_width=True)

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Daily Footfall")

        if not daily.empty:
            fig_daily = px.bar(
                daily,
                x="Date",
                y="TotalVisits",
                text="TotalVisits",
                title="Daily Visits",
            )

            st.plotly_chart(
                fig_daily,
                use_container_width=True,
            )
        else:
            st.info("No daily footfall data available.")

    with right:
        st.subheader("Store Peak Hours")

        if not peaks.empty:
            display_peaks = peaks.copy()
            display_peaks["PeakHour"] = (
                display_peaks["PeakHour"].astype(str)
                + ":00"
            )

            st.dataframe(
                display_peaks,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No peak-hour data available.")

    st.divider()

    st.subheader("Store Footfall Details")

    st.dataframe(
        metrics,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Detected Visit Sessions")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"GPS observations: {len(gps):,} | "
        f"Detected sessions: {len(sessions):,} | "
        f"Dataset: {GPS_PATH.name}"
    )

    st.info(
        "Analytics are based on detected GPS visit sessions. "
        "GPS observations represent devices, not verified human visitors. "
        "The current dataset covers one date only."
    )

except Exception as exc:
    st.error(f"Dashboard could not load: {exc}")
    st.exception(exc)
