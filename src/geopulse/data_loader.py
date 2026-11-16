
import pandas as pd

from .config import (
    GPS_DATA_PATH,
    STORE_DATA_PATH,
    CATCHMENT_DATA_PATH
)


def load_gps_data():
    return pd.read_csv(GPS_DATA_PATH)


def load_store_data():
    return pd.read_csv(STORE_DATA_PATH)


def load_catchment_data():
    return pd.read_csv(CATCHMENT_DATA_PATH)
