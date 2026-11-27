
import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from geopulse.footfall import detect_visit_sessions
from geopulse.temporal import (
    analyze_hourly_footfall,
    analyze_daily_footfall,
    compare_weekday_weekend_footfall,
    analyze_store_peak_hours,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate temporal mobility analysis reports for GeoPulse."
    )

    parser.add_argument(
        "--gps",
        type=Path,
        default=Path("data/geopulse_gps_trajectories.csv"),
        help="Input GPS trajectories CSV path.",
    )

    parser.add_argument(
        "--stores",
        type=Path,
        default=Path("data/geopulse_store_locations.csv"),
        help="Input store locations CSV path.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/temporal_analysis"),
        help="Output directory for temporal CSV reports.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing report files.",
    )

    args = parser.parse_args()

    gps_path = args.gps
    stores_path = args.stores
    output_dir = args.output

    if not gps_path.is_absolute():
        gps_path = PROJECT_ROOT / gps_path

    if not stores_path.is_absolute():
        stores_path = PROJECT_ROOT / stores_path

    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir

    for input_path in [gps_path, stores_path]:
        if not input_path.exists():
            parser.error(f"Input dataset does not exist: {input_path}")

        if not input_path.is_file():
            parser.error(f"Input path is not a file: {input_path}")

    report_names = [
        "hourly_footfall.csv",
        "daily_footfall.csv",
        "weekday_weekend_comparison.csv",
        "store_peak_hours.csv",
    ]

    existing_reports = [
        output_dir / name
        for name in report_names
        if (output_dir / name).exists()
    ]

    if existing_reports and not args.overwrite:
        parser.error(
            "Report files already exist. Use --overwrite to replace them: "
            + ", ".join(str(path) for path in existing_reports)
        )

    try:
        gps_data = pd.read_csv(gps_path)
        stores = pd.read_csv(stores_path)

        sessions = detect_visit_sessions(gps_data, stores)

        reports = {
            "hourly_footfall.csv": analyze_hourly_footfall(sessions),
            "daily_footfall.csv": analyze_daily_footfall(sessions),
            "weekday_weekend_comparison.csv": (
                compare_weekday_weekend_footfall(sessions)
            ),
            "store_peak_hours.csv": analyze_store_peak_hours(sessions),
        }

        output_dir.mkdir(parents=True, exist_ok=True)

        for filename, report in reports.items():
            report.to_csv(output_dir / filename, index=False)

        print("\nGeoPulse Temporal Analysis Reports Generated")
        print("-" * 48)
        print(f"GPS observations : {len(gps_data)}")
        print(f"Stores            : {len(stores)}")
        print(f"Detected visits   : {len(sessions)}")
        print(f"Reports generated : {len(reports)}")
        print(f"Output directory  : {output_dir}")

        for filename, report in reports.items():
            print(f"{filename:<34}: {len(report)} rows")

    except (
        ValueError,
        TypeError,
        OSError,
        pd.errors.ParserError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
