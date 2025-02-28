import pytest
import pandas as pd
import io
from src.data_cleaning import clean_csv_data, clean_json_data, clean_excel_data

@pytest.fixture
def csv_data():
    return b"col1, col2 , col3\n1,2,3\n4,5,6\n1,2,3\n\n"

@pytest.fixture
def json_data():
    return b'[{"col1": 1, "col2": 2}, {"col1": 1, "col2": 2}, {"col1": 3, "col2": 4}]'

@pytest.fixture
def excel_data():
    df = pd.DataFrame({"col1": [1, 1, 3], "col2": [2, 2, 4]})
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='xlsxwriter')
    return output.getvalue()

def test_clean_csv_data(csv_data):
    cleaned = clean_csv_data(csv_data)
    assert b"col1,col2,col3\n1,2,3\n4,5,6\n" in cleaned

def test_clean_json_data(json_data):
    cleaned = clean_json_data(json_data)
    assert b'{"col1":1,"col2":2}' in cleaned
    assert b'{"col1":3,"col2":4}' in cleaned

def test_clean_excel_data(excel_data):
    cleaned = clean_excel_data(excel_data)
    df = pd.read_excel(io.BytesIO(cleaned))
    assert df.shape == (2, 2)  # Vérifie qu'on a bien supprimé les doublons
