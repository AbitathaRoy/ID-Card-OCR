# src/sheet_reader.py

import pandas as pd
from src.sheet_config import SHEET_EXPORT_URL


def read_responses():
    """
    Reads Google Form responses into a DataFrame.
    """
    df = pd.read_excel(SHEET_EXPORT_URL)
    return df
