
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from geopulse.gps_generator import save_gps_data
from geopulse.stop_data_generator import generate_stop_scenario_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic GPS stop scenario data."
    )

    parser.add_argument(
        "--num-devices",
        type=int,
        default=20,
        help="Number of devices to generate (default: 20).",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "geopulse_stop_scenarios.csv",
        help="Output CSV file path.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing output file.",
    )

    args = parser.parse_args()

    gps_data = generate_stop_scenario_data(
        num_devices=args.num_devices,
        seed=args.seed,
    )

    output_path = args.output

    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    save_gps_data(
        gps_data,
        output_path,
        overwrite=args.overwrite,
    )

    print("GPS stop scenario data generated successfully.")
    print(f"Devices: {gps_data['DeviceID'].nunique()}")
    print(f"Records: {len(gps_data)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
