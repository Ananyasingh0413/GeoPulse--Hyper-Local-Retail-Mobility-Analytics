
import json

import pandas as pd
import pytest

from geopulse.eda import (
    generate_dataset_overview,
    analyze_missing_values,
    analyze_duplicates,
    profile_columns,
    generate_eda_report,
    save_eda_report,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "DeviceID": ["D1", "D2", "D2", "D3"],
        "Lat": [28.61, 28.62, 28.62, 28.63],
        "Long": [77.20, 77.21, 77.21, None],
        "Category": ["A", "B", "B", "A"],
    })


def test_dataset_overview(sample_data):
    result = generate_dataset_overview(sample_data)

    assert result["total_rows"] == 4
    assert result["total_columns"] == 4
    assert "DeviceID" in result["columns"]
    assert result["memory_usage_bytes"] > 0


def test_missing_value_analysis(sample_data):
    result = analyze_missing_values(sample_data)

    assert result["Long"]["missing_count"] == 1
    assert result["Long"]["missing_percentage"] == 25.0
    assert result["Lat"]["missing_count"] == 0


def test_duplicate_analysis(sample_data):
    result = analyze_duplicates(sample_data)

    assert result["duplicate_rows"] == 1
    assert result["duplicate_percentage"] == 25.0


def test_column_profiles(sample_data):
    result = profile_columns(sample_data)

    assert result["Lat"]["data_type"] == "float64"
    assert result["Lat"]["non_null_count"] == 4
    assert result["Lat"]["unique_values"] == 3
    assert "statistics" in result["Lat"]
    assert "top_values" in result["Category"]


def test_complete_eda_report(sample_data):
    result = generate_eda_report(sample_data)

    assert "dataset_overview" in result
    assert "missing_values" in result
    assert "duplicate_analysis" in result
    assert "column_profiles" in result


def test_save_eda_report(tmp_path, sample_data):
    report = generate_eda_report(sample_data)
    output = tmp_path / "nested" / "eda_report.json"

    saved_path = save_eda_report(report, output)

    assert saved_path.exists()

    with saved_path.open(encoding="utf-8") as file:
        loaded = json.load(file)

    assert loaded["dataset_overview"]["total_rows"] == 4


@pytest.mark.parametrize(
    "function",
    [
        generate_dataset_overview,
        analyze_missing_values,
        analyze_duplicates,
        profile_columns,
    ],
)
def test_empty_dataframe_rejected(function):
    with pytest.raises(ValueError):
        function(pd.DataFrame())


@pytest.mark.parametrize(
    "function",
    [
        generate_dataset_overview,
        analyze_missing_values,
        analyze_duplicates,
        profile_columns,
    ],
)
def test_invalid_input_rejected(function):
    with pytest.raises(TypeError):
        function(["invalid"])


def test_invalid_report_rejected():
    with pytest.raises(TypeError):
        save_eda_report([], "report.json")
