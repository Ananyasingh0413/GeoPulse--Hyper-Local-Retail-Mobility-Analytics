
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from geopulse.gps_generator import generate_gps_data, save_gps_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic GeoPulse GPS mobility data."
    )

    parser.add_argument(
        "--records", type=int, default=1000,
        help="Number of GPS records (default: 1000)"
    )
    parser.add_argument(
        "--devices", type=int, default=100,
        help="Number of unique devices (default: 100)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--start", default="2026-11-01",
        help="Start timestamp"
    )
    parser.add_argument(
        "--end", default="2026-11-05",
        help="End timestamp"
    )
    parser.add_argument(
        "--output",
        default="data/geopulse_gps_generated.csv",
        help="CSV output path"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Allow replacing an existing output file"
    )

    args = parser.parse_args()

    try:
        gps_data = generate_gps_data(
            num_records=args.records,
            num_devices=args.devices,
            start_time=args.start,
            end_time=args.end,
            seed=args.seed,
        )

        output_path = Path(args.output)

        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path

        saved_path = save_gps_data(
            gps_data,
            output_path,
            overwrite=args.overwrite,
        )

        print("\nGeoPulse GPS Data Generated Successfully")
        print("-" * 45)
        print(f"Total records : {len(gps_data)}")
        print(f"Unique devices: {gps_data['DeviceID'].nunique()}")
        print(f"Output file   : {saved_path}")
        print("\nDataset preview:")
        print(gps_data.head())

    except (ValueError, TypeError, FileExistsError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
