"""
Data Preprocessing Module for Sales Forecasting System
Handles data validation, cleaning, missing value imputation, 
daily aggregation, and time/lag feature engineering.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def validate_and_clean_dataframe(df):
    """
    Validates the uploaded or imported sales dataframe.
    Ensures required columns ('Date', 'Sales') exist (case-insensitive).
    Cleans data, removes duplicates, handles missing values, and standardizes types.
    
    Returns:
        tuple: (cleaned_df, error_message)
    """
    if df is None or df.empty:
        return None, "Dataset is empty. Please provide a valid CSV with data."

    # Normalize column names (strip whitespace and match case-insensitively)
    col_mapping = {}
    for col in df.columns:
        clean_name = str(col).strip()
        lower_name = clean_name.lower()
        if lower_name == "date":
            col_mapping[col] = "Date"
        elif lower_name in ["sales", "sale", "total_sales", "amount", "revenue"]:
            col_mapping[col] = "Sales"
        elif lower_name in ["product", "product_name", "item"]:
            col_mapping[col] = "Product"
        elif lower_name in ["category", "cat"]:
            col_mapping[col] = "Category"
        elif lower_name in ["quantity", "qty", "units", "units_sold"]:
            col_mapping[col] = "Quantity"
        elif lower_name in ["unit_price", "price", "unitprice"]:
            col_mapping[col] = "Unit_Price"

    df = df.rename(columns=col_mapping)

    # Check mandatory columns
    required_cols = ["Date", "Sales"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return None, "Invalid dataset. Please upload a CSV containing Date and Sales columns."

    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Convert Date column
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    except Exception as e:
        return None, f"Failed to parse dates in 'Date' column: {str(e)}"

    # Drop rows with invalid or missing Date
    df = df.dropna(subset=["Date"])
    if df.empty:
        return None, "All date values in 'Date' column could not be parsed."

    # Convert Sales to numeric
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df = df.dropna(subset=["Sales"])
    # Remove negative sales or invalid values
    df = df[df["Sales"] >= 0]

    if df.empty:
        return None, "No valid positive sales records found in dataset."

    # Standardize optional columns if they exist, or set sensible defaults
    if "Product" not in df.columns or df["Product"].isnull().all():
        df["Product"] = "General Product"
    else:
        df["Product"] = df["Product"].fillna("Unspecified").astype(str).str.strip()

    if "Category" not in df.columns or df["Category"].isnull().all():
        df["Category"] = "General"
    else:
        df["Category"] = df["Category"].fillna("General").astype(str).str.strip()

    if "Quantity" not in df.columns:
        df["Quantity"] = 1
    else:
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(1).astype(int)
        df.loc[df["Quantity"] <= 0, "Quantity"] = 1

    if "Unit_Price" not in df.columns:
        df["Unit_Price"] = (df["Sales"] / df["Quantity"]).round(2)
    else:
        df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")
        # Impute missing unit prices
        df["Unit_Price"] = df["Unit_Price"].fillna((df["Sales"] / df["Quantity"]).round(2))
        df.loc[df["Unit_Price"] < 0, "Unit_Price"] = 0.0

    # Remove duplicates
    df = df.drop_duplicates()

    # Format Date as standard YYYY-MM-DD string and sort chronologically
    df["Date_dt"] = df["Date"]
    df["Date"] = df["Date_dt"].dt.strftime("%Y-%m-%d")
    df = df.sort_values(by="Date_dt").reset_index(drop=True)
    df = df.drop(columns=["Date_dt"])

    # Ensure sufficient records
    if len(df) < 15:
        return None, "Dataset contains fewer than 15 valid records. More data is required for forecasting."

    return df, None


def aggregate_daily_sales(df):
    """
    Aggregates individual transaction records into a daily time series.
    Fills missing calendar dates with 0 so the daily time series has continuous lag integrity.
    
    Returns:
        pd.DataFrame with columns ['Date', 'Sales', 'Quantity']
    """
    daily = df.groupby("Date").agg({
        "Sales": "sum",
        "Quantity": "sum"
    }).reset_index()

    daily["Date"] = pd.to_datetime(daily["Date"])
    daily = daily.sort_values(by="Date").reset_index(drop=True)

    # Reindex to full date range
    min_date = daily["Date"].min()
    max_date = daily["Date"].max()
    full_idx = pd.date_range(start=min_date, end=max_date, freq="D")
    
    daily = daily.set_index("Date").reindex(full_idx)
    # Missing days mean 0 sales
    daily["Sales"] = daily["Sales"].fillna(0.0)
    daily["Quantity"] = daily["Quantity"].fillna(0)
    daily = daily.reset_index().rename(columns={"index": "Date"})
    daily["Date_str"] = daily["Date"].dt.strftime("%Y-%m-%d")
    
    return daily


def create_time_and_lag_features(daily_df):
    """
    Extracts time-based and autoregressive lag features for machine learning.
    
    Time Features:
        - year, month, day, day_of_week (0=Mon..6=Sun), is_weekend, day_of_year
    Lag Features:
        - lag_1: Sales 1 day ago (yesterday)
        - lag_7: Sales 7 days ago (same day last week)
        - lag_14: Sales 14 days ago
        - rolling_mean_7: 7-day moving average of sales (shifted by 1 to prevent target leakage)
    
    Returns:
        tuple: (features_df, feature_column_names)
    """
    df = daily_df.copy()
    
    # Time-based features
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day
    df["day_of_week"] = df["Date"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
    df["day_of_year"] = df["Date"].dt.dayofyear

    # Lag features
    df["lag_1"] = df["Sales"].shift(1)
    df["lag_7"] = df["Sales"].shift(7)
    df["lag_14"] = df["Sales"].shift(14)
    
    # 7-day rolling mean (shifted by 1 day to ensure only past information is used)
    df["rolling_mean_7"] = df["Sales"].shift(1).rolling(window=7, min_periods=1).mean()

    feature_cols = [
        "year", "month", "day", "day_of_week", "is_weekend", "day_of_year",
        "lag_1", "lag_7", "lag_14", "rolling_mean_7"
    ]

    # Drop rows with NaN from lag shifts (first 14 rows)
    clean_features_df = df.dropna(subset=feature_cols).reset_index(drop=True)
    
    return clean_features_df, feature_cols
