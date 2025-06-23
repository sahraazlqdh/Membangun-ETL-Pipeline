import pytest
import pandas as pd
from utils.transform import clean_and_transform
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_clean_and_transform_valid():
    df = pd.DataFrame({
        "Title": ["Item A"],
        "Price": ["$20.00"],
        "Rating": ["⭐ 4.5"],
        "Colors": ["3 Colors"],
        "Size": ["M"],
        "Gender": ["Male"],
        "Timestamp": ["2025-05-10T10:00:00"]
    })
    result = clean_and_transform(df)
    assert not result.empty
    assert result["Price"].iloc[0] == 320000.0
    assert result["Rating"].iloc[0] == 4.5

def test_clean_and_transform_invalid_rating():
    df = pd.DataFrame({
        "Title": ["Item A"],
        "Price": ["$10.00"],
        "Rating": ["Invalid Rating"],
        "Colors": ["3 Colors"],
        "Size": ["M"],
        "Gender": ["Male"],
        "Timestamp": ["2025-05-10T10:00:00"]
    })
    result = clean_and_transform(df)
    assert result.empty

def test_clean_and_transform_invalid_price():
    df = pd.DataFrame({
        "Title": ["Item A"],
        "Price": ["INVALID"],
        "Rating": ["⭐ 4.5"],
        "Colors": ["3 Colors"],
        "Size": ["M"],
        "Gender": ["Male"],
        "Timestamp": ["2025-05-10T10:00:00"]
    })
    result = clean_and_transform(df)
    assert result.empty
