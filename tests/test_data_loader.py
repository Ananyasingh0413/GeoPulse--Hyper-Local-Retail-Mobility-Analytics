
import pandas as pd
import pytest

from geopulse.data_loader import (
    _load_csv,
    load_gps_data,
    load_store_data,
    load_catchment_data,
    load_custom_csv,
)


def test_load_valid_csv(tmp_path):
    file = tmp_path / "sample.csv"
    pd.DataFrame({"ID": [1, 2]}).to_csv(file, index=False)

    result = _load_csv(file)

    assert len(result) == 2
    assert list(result.columns) == ["ID"]


def test_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        _load_csv(tmp_path / "missing.csv")


def test_empty_file_raises_error(tmp_path):
    file = tmp_path / "empty.csv"
    file.touch()

    with pytest.raises(ValueError, match="empty"):
        _load_csv(file)


def test_header_only_csv_raises_error(tmp_path):
    file = tmp_path / "header.csv"
    file.write_text("ID,Name\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no records"):
        _load_csv(file)


def test_missing_required_columns_raises_error(tmp_path):
    file = tmp_path / "sample.csv"
    pd.DataFrame({"ID": [1]}).to_csv(file, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        _load_csv(file, ["ID", "Name"])


def test_malformed_csv_raises_error(tmp_path):
    file = tmp_path / "malformed.csv"
    file.write_text("ID,Name\n1,A\n2,B,Extra\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid CSV structure"):
        _load_csv(file)


def test_utf8_bom_is_supported(tmp_path):
    file = tmp_path / "bom.csv"
    file.write_text(
        "\ufeffID,Name\n1,Rahul\n",
        encoding="utf-8"
    )

    result = _load_csv(file)

    assert "ID" in result.columns
    assert result.iloc[0]["Name"] == "Rahul"


def test_custom_csv_loader(tmp_path):
    file = tmp_path / "custom.csv"
    pd.DataFrame({"Code": [101], "Name": ["Store"]}).to_csv(
        file, index=False
    )

    result = load_custom_csv(file, ["Code", "Name"])

    assert result.iloc[0]["Code"] == 101


def test_custom_csv_loader_rejects_missing_columns(tmp_path):
    file = tmp_path / "custom.csv"
    pd.DataFrame({"Code": [101]}).to_csv(file, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        load_custom_csv(file, ["Code", "Name"])


def test_load_gps_data():
    result = load_gps_data()

    assert not result.empty
    assert {"DeviceID", "Lat", "Long", "Timestamp"}.issubset(result.columns)


def test_load_store_data():
    result = load_store_data()

    assert not result.empty
    assert {"StoreID", "StoreName", "Lat", "Long"}.issubset(result.columns)


def test_load_catchment_data():
    result = load_catchment_data()

    assert not result.empty
