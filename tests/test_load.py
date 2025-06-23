"""
test_load.py
Unit tests untuk tahap Load dalam ETL pipeline:
- Menyimpan ke CSV
- Menyimpan ke PostgreSQL
- Menyimpan ke Google Sheets
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Menambahkan direktori proyek ke sys.path agar modul utils bisa diimpor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.load import save_to_csv, save_to_postgresql, save_to_google_spreadsheet, load_data

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Title": ["Item A"],
        "Price": [160000.0],
        "Rating": [4.5],
        "Colors": [3],
        "Size": ["M"],
        "Gender": ["Male"],
        "Timestamp": ["2025-05-10T10:00:00"]
    })

def test_save_to_csv(tmp_path, sample_dataframe):
    file_path = tmp_path / "output.csv"
    save_to_csv(sample_dataframe, filename=str(file_path))
    df = pd.read_csv(file_path)
    assert not df.empty
    assert df.equals(sample_dataframe)

@patch("pandas.DataFrame.to_csv", side_effect=Exception("Failed"))
def test_save_to_csv_error(mock_to_csv, capsys, sample_dataframe):
    save_to_csv(sample_dataframe, filename="broken.csv")
    captured = capsys.readouterr()
    assert "[CSV Error]" in captured.out

@patch("utils.load.create_engine")
def test_save_to_postgresql(mock_create_engine, sample_dataframe):
    engine_mock = MagicMock()
    mock_create_engine.return_value = engine_mock

    with patch.object(sample_dataframe, "to_sql") as mock_to_sql:
        save_to_postgresql(sample_dataframe, "db", "user", "pass")
        mock_to_sql.assert_called_once_with("fashion_products", engine_mock, index=False, if_exists="replace")

@patch("utils.load.create_engine", side_effect=Exception("Connection failed"))
def test_save_to_postgresql_error(mock_engine, capsys, sample_dataframe):
    save_to_postgresql(sample_dataframe, "db", "user", "pass")
    captured = capsys.readouterr()
    assert "[PostgreSQL Error]" in captured.out

@patch("utils.load.Credentials.from_service_account_file")
@patch("utils.load.build")
def test_save_to_google_spreadsheet(mock_build, mock_creds, sample_dataframe):
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    sheet = mock_service.spreadsheets.return_value
    values = sheet.values.return_value
    values.clear.return_value.execute.return_value = None
    values.update.return_value.execute.return_value = None

    save_to_google_spreadsheet(
        sample_dataframe,
        spreadsheet_id="dummy_id",
        range_name="Sheet1!A1",
        credential_file="fake.json"
    )

    values.clear.assert_called_once()
    values.update.assert_called_once()

@patch("utils.load.Credentials.from_service_account_file", side_effect=Exception("Auth failed"))
def test_save_to_google_spreadsheet_error(_mock_creds, sample_dataframe, capsys):
    save_to_google_spreadsheet(
        sample_dataframe,
        spreadsheet_id="dummy_id",
        range_name="Sheet1!A1",
        credential_file="fake.json"
    )
    captured = capsys.readouterr()
    assert "[Google Sheets Error]" in captured.out

@patch("utils.load.save_to_csv")
@patch("utils.load.save_to_postgresql")
@patch("utils.load.save_to_google_spreadsheet")
def test_load_data(mock_gsheet, mock_pg, mock_csv, sample_dataframe):
    load_data(
        sample_dataframe,
        spreadsheet_id="dummy_id",      
        range_name="Sheet1!A1",
        credential_file="fake.json"
    )
    mock_csv.assert_called_once()
    mock_pg.assert_called_once()
    mock_gsheet.assert_called_once()