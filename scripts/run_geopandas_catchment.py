
import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from geopulse.spatial import analyze_spatial_catchments
from geopulse.config import CATCHMENT_RADIUS_METERS


def main():
    parser = argparse.ArgumentParser(
        description="Run GeoPandas-based store catchment analysis."
    )

    parser.add_argument(
        "--gps",
        type=Path,
        default=Path("data/geopulse_gps_trajectories.csv"),
        help="Input GPS trajectories CSV."
    )

    parser.add_argument(
        "--stores",
        type=Path,
        default=Path("data/geopulse_store_locations.csv"),
        help="Input store locations CSV."
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/geopandas_catchment"),
        help="Directory for output CSV files."
    )

    parser.add_argument(
        "--radius",
        type=float,
        default=CATCHMENT_RADIUS_METERS,
        help="Store catchment radius in metres."
    )

    parser.add_argument(
        "--crs",
        type=str,
        default="EPSG:32643",
        help="Projected CRS to use for distance calculations (default: EPSG:32643)."
    )

    args = parser.parse_args()

    gps_path = args.gps
    stores_path = args.stores
    output_dir = args.output_dir

    if not gps_path.is_absolute():
        gps_path = PROJECT_ROOT / gps_path

    if not stores_path.is_absolute():
        stores_path = PROJECT_ROOT / stores_path

    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir

    for input_path in [gps_path, stores_path]:
        if not input_path.exists():
            parser.error(
                f"Input dataset does not exist: {input_path}"
            )

        if not input_path.is_file():
            parser.error(
                f"Input path is not a file: {input_path}"
            )

    try:
        gps = pd.read_csv(gps_path)
        stores = pd.read_csv(stores_path)

        matches, unmatched, summary = (
            analyze_spatial_catchments(
                gps,
                stores,
                radius_meters=args.radius,
                projected_crs=args.crs
            )
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        matches_path = (
            output_dir / "geopulse_spatial_matches.csv"
        )
        unmatched_path = (
            output_dir / "geopulse_spatial_unmatched.csv"
        )
        summary_path = (
            output_dir / "geopulse_spatial_summary.csv"
        )

        matches.to_csv(matches_path, index=False)
        unmatched.to_csv(unmatched_path, index=False)
        summary.to_csv(summary_path, index=False)

        print("\nGeoPulse GeoPandas Catchment Analysis")
        print("-" * 45)
        print(f"GPS records       : {len(gps)}")
        print(f"Store locations   : {len(stores)}")
        print(f"Catchment radius  : {args.radius} metres")
        print(f"Projected CRS     : {args.crs}")
        print(f"Matched records   : {len(matches)}")
        print(f"Unmatched records : {len(unmatched)}")
        print(
            "Unique devices    : "
            f"{matches['DeviceID'].nunique()}"
        )
        print(
            "Total store visits: "
            f"{summary['Total_GPS_Visits'].sum()}"
        )
        print(f"\nOutput directory  : {output_dir}")
        print(f"Matches           : {matches_path.name}")
        print(f"Unmatched         : {unmatched_path.name}")
        print(f"Summary           : {summary_path.name}")

    except (
        ValueError,
        TypeError,
        OSError,
        pd.errors.ParserError
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
