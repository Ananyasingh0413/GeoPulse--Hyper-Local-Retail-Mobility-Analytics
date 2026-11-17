
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Main project directories
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Dataset paths
GPS_DATA_PATH = DATA_DIR / "geopulse_gps_data.csv"
STORE_DATA_PATH = DATA_DIR / "geopulse_store_locations.csv"
CATCHMENT_DATA_PATH = DATA_DIR / "geopulse_catchment_analysis.csv"

# Geographic configuration
CATCHMENT_RADIUS_METERS = 500

# Required GPS columns
GPS_REQUIRED_COLUMNS = [
    "DeviceID",
    "Lat",
    "Long",
    "Timestamp"
]

# Required Store columns
STORE_REQUIRED_COLUMNS = [
    "StoreID",
    "StoreName",
    "Lat",
    "Long"
]
