
from pathlib import Path
import json

import pandas as pd


def generate_dataset_overview(data):
    """Generate a structural overview of a dataset."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if data.empty:
        raise ValueError("Dataset cannot be empty.")

    return {
        "total_rows": int(data.shape[0]),
        "total_columns": int(data.shape[1]),
        "columns": data.columns.tolist(),
        "memory_usage_bytes": int(
            data.memory_usage(deep=True).sum()
        ),
    }


def analyze_missing_values(data):
    """Calculate missing-value counts and percentages."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if data.empty:
        raise ValueError("Dataset cannot be empty.")

    missing_count = data.isna().sum()

    return {
        column: {
            "missing_count": int(missing_count[column]),
            "missing_percentage": round(
                float(missing_count[column] / len(data) * 100),
                2
            ),
        }
        for column in data.columns
    }


def analyze_duplicates(data):
    """Analyze duplicate records in a dataset."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if data.empty:
        raise ValueError("Dataset cannot be empty.")

    duplicate_count = int(data.duplicated().sum())

    return {
        "duplicate_rows": duplicate_count,
        "duplicate_percentage": round(
            duplicate_count / len(data) * 100, 2
        ),
    }


def profile_columns(data):
    """Generate descriptive profiles for individual columns."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if data.empty:
        raise ValueError("Dataset cannot be empty.")

    profiles = {}

    for column in data.columns:
        series = data[column]

        profiles[column] = {
            "data_type": str(series.dtype),
            "non_null_count": int(series.count()),
            "unique_values": int(series.nunique()),
        }

        if pd.api.types.is_numeric_dtype(series):
            profiles[column]["statistics"] = (
                series.describe().to_dict()
            )

        else:
            profiles[column]["top_values"] = (
                series.value_counts().head(5).to_dict()
            )

    return profiles


def generate_eda_report(data):
    """Generate a complete exploratory data analysis report."""
    return {
        "dataset_overview": generate_dataset_overview(data),
        "missing_values": analyze_missing_values(data),
        "duplicate_analysis": analyze_duplicates(data),
        "column_profiles": profile_columns(data),
    }


def save_eda_report(report, output_path):
    """Save an EDA report as a JSON file."""
    if not isinstance(report, dict):
        raise TypeError("Report must be a dictionary.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            default=str,
            allow_nan=False
        )

    return path
