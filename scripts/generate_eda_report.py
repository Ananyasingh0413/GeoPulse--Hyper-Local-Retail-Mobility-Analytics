
import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from geopulse.eda import generate_eda_report, save_eda_report


def main():
    parser = argparse.ArgumentParser(
        description="Generate an exploratory data analysis report for GeoPulse datasets."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input CSV dataset path.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON report path.",
    )

    args = parser.parse_args()

    input_path = args.input

    if not input_path.is_absolute():
        input_path = PROJECT_ROOT / input_path

    if not input_path.exists():
        parser.error(f"Input dataset does not exist: {input_path}")

    if not input_path.is_file():
        parser.error(f"Input path is not a file: {input_path}")

    output_path = args.output

    if output_path is None:
        output_path = (
            PROJECT_ROOT
            / "reports"
            / f"{input_path.stem}_eda_report.json"
        )
    elif not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    try:
        data = pd.read_csv(input_path)
        report = generate_eda_report(data)
        saved_path = save_eda_report(report, output_path)

        overview = report["dataset_overview"]
        missing = sum(
            item["missing_count"]
            for item in report["missing_values"].values()
        )

        print("\nGeoPulse EDA Report Generated Successfully")
        print("-" * 45)
        print(f"Dataset       : {input_path.name}")
        print(f"Total records : {overview['total_rows']}")
        print(f"Total columns : {overview['total_columns']}")
        print(f"Missing values: {missing}")
        print(
            "Duplicate rows: "
            f"{report['duplicate_analysis']['duplicate_rows']}"
        )
        print(f"Report saved  : {saved_path}")

    except (ValueError, TypeError, OSError, pd.errors.ParserError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
