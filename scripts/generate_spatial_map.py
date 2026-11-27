
import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from geopulse.visualization import generate_spatial_map
from geopulse.config import CATCHMENT_RADIUS_METERS


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive GeoPulse spatial map."
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
        "--output",
        type=Path,
        default=Path("reports/geopulse_spatial_map.html"),
        help="Output HTML map path."
    )

    parser.add_argument(
        "--radius",
        type=float,
        default=CATCHMENT_RADIUS_METERS,
        help="Store catchment radius in metres."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output file."
    )

    args = parser.parse_args()

    gps_path = args.gps
    stores_path = args.stores
    output_path = args.output

    if not gps_path.is_absolute():
        gps_path = PROJECT_ROOT / gps_path

    if not stores_path.is_absolute():
        stores_path = PROJECT_ROOT / stores_path

    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    for input_path in [gps_path, stores_path]:
        if not input_path.exists():
            parser.error(
                f"Input dataset does not exist: {input_path}"
            )

        if not input_path.is_file():
            parser.error(
                f"Input path is not a file: {input_path}"
            )

    if output_path.exists() and not args.overwrite:
        parser.error(
            f"Output already exists: {output_path}. "
            "Use --overwrite to replace it."
        )

    try:
        gps = pd.read_csv(gps_path)
        stores = pd.read_csv(stores_path)

        generate_spatial_map(
            gps,
            stores,
            output_path,
            radius_meters=args.radius
        )

        print("\nGeoPulse Interactive Spatial Map")
        print("-" * 45)
        print(f"GPS observations  : {len(gps)}")
        print(f"Store locations   : {len(stores)}")
        print(f"Catchment radius  : {args.radius} metres")
        print(f"Output file       : {output_path}")
        print(f"File size         : {output_path.stat().st_size:,} bytes")
        print("\nMap generated successfully.")

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
